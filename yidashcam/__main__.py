#!/usr/bin/env python
"""Command line tool for interaction with YI Dashcam"""

import argparse
import enum
import sys
import time

from . import __version__, YIDashcam
from .config import Option, option_map, PhotoResolution


def format_config(option, value):
    return "{0}: {1}".format(
        option.name.replace("_", " ").title(),
        value.name.replace("_", " ").title()
        if hasattr(value, 'name') else value)


parser = argparse.ArgumentParser(prog=YIDashcam.__module__)
parser.add_argument(
    '--version', action='version', version='%(prog)s v{}'.format(__version__))
subparsers = parser.add_subparsers(
    title="Commands", dest='command', metavar='COMMAND')

#  Config
parser_config = subparsers.add_parser(
    'config', help='camera information and configuration')
subparsers_config = parser_config.add_subparsers(
    title="Config options", dest='option', metavar='')
for option, val_type in sorted(option_map.items(), key=lambda x: x[0].name):
    if val_type is str:
        continue
    parser_option = subparsers_config.add_parser(
        option.name, help=option.name.replace('_', ' ').title())
    if issubclass(val_type, enum.Enum):
        parser_option.add_argument(
            'value', choices=[value.name for value in val_type])
    elif val_type is bool:
        parser_option.add_argument(
            'value', type=str.lower, choices=['true', 'false'])

#  Video stream
parser_stream = subparsers.add_parser(
    'stream', help='put dashcam in mode to stream video')

#  Photo capture
parser_snapshot = subparsers.add_parser(
    'snapshot', help='take a photo with the dashcam')
parser_snapshot.add_argument(
    '-r',
    dest='photo_resolution',
    choices=[res.name for res in PhotoResolution],
    help="photo resolution (default: dashcam current setting)")
parser_snapshot.add_argument(
    '-o',
    dest='output_filename',
    metavar="FILE",
    help="output file to save image (default: filename on camera)")

# Web Application
parser_config = subparsers.add_parser(
    'webapp', help='host local web app to view dashcam videos')

if "exposure" in sys.argv:
    #  Allow negative values for exposure
    sys.argv.insert(len(sys.argv) - 1, "--")
args = parser.parse_args()

if args.command is None or args.command == "config":
    with YIDashcam() as yi:
        if getattr(args, 'option', None) is not None:
            option = Option[args.option]
            val_type = option_map[option]
            time.sleep(1)  #  Need a chance for dashcam to settle...
            if issubclass(val_type, enum.Enum):
                yi.set_config(option, val_type[args.value])
            elif val_type is bool:
                yi.set_config(option, args.value.lower() == "true")
            time.sleep(1)  #  Need a chance for config to set...
            print(format_config(option, yi.config[option]))
        else:
            print(
                *[format_config(option, value)
                  for option, value in sorted(
                      yi.config.items(), key=lambda x: x[0].name)],
                sep="\n")
elif args.command == "stream":
    with YIDashcam() as yi:
        print("Connect to video stream at: rtsp://{0.HOST}/xxx.mov".format(yi))
        try:
            while yi.connected:
                time.sleep(0.1)
        except KeyboardInterrupt:
            pass
elif args.command == "snapshot":
    with YIDashcam() as yi:
        if args.photo_resolution is not None:
            time.sleep(1)  #  Need a chance for dashcam to settle...
            yi.set_config(Option.photo_resolution,
                          PhotoResolution[args.photo_resolution])
        yi.take_photo()
        photo = sorted(yi.photo_list)[-1]
        if args.output_filename is None:
            output_filename = photo.name
        else:
            output_filename = args.output_filename
        with open(output_filename, 'wb') as output_file:
            for data in yi.get_file(photo):
                output_file.write(data)
        print("Snapshot saved to: {}".format(output_filename))
elif args.command == "webapp":
    from . import webapp
    with YIDashcam(None) as yi:
        webapp.yi = yi
        webapp.app.run()
