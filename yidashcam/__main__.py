#!/usr/bin/env python
"""Put YI Dashcam in stream mode"""

import sys
import time

from . import YIDashcam
from .config import Option, PhotoResolution

with YIDashcam() as yi:
    print("Model: {0.model}\n"
          "Serial Number: {0.serial_number}\n"
          "Firmware Version: {0.firmware_version}".format(yi))
    if len(sys.argv) <= 1 or sys.argv[1].lower() == "stream":
        print("Connect to video stream at: rtsp://{0.HOST}/xxx.mov".format(yi))
        try:
            while yi.connected:
                time.sleep(0.1)
        except KeyboardInterrupt:
            pass
    elif sys.argv[1].lower() == "snapshot":
        yi.set_config(Option.photo_resolution, PhotoResolution.r1920x1080)
        photo = yi.take_photo()
        with open(photo.name, 'wb') as local_file:
            for data in yi.get_file(photo):
                local_file.write(data)
        print("Snapshot save to: {0.name}".format(photo))
    else:
        print("Unknown command: {}".format(sys.argv[1]))
