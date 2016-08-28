#!/usr/bin/env python

from flask import Flask, Response, render_template

import yidashcam

app = Flask(__name__)
yi = None


@app.before_first_request
def connect_yi():
    global yi
    yi = yidashcam.YIDashcam(mode=yidashcam.Mode.file)


def get_yi():
    if not yi.connected:
        yi.connect(mode=yidashcam.Mode.file)
    return yi


@app.errorhandler(yidashcam.YIDashcamConnectionException)
def yi_connection_handler(error):
    return "Failed to connect to YI Dashcam", 500


@app.errorhandler(yidashcam.YIDashcamFileException)
def yi_file_handler(error):
    return "File not found on YI Dashcam", 404


@app.route('/')
@app.route('/emergency')
def emergency_list():
    return render_template('file_list.html', file_list=get_yi().emergency_list)


@app.route('/roadmap')
def roadmap_list():
    return render_template('file_list.html', file_list=get_yi().roadmap_list)


@app.route('/photo')
def photo_list():
    return render_template('file_list.html', file_list=get_yi().photo_list)


@app.route('/thumbnail/<path:path>')
def thumbnail(path):
    """Fetch thumbnail, and ask browser to cache for a week"""
    return Response(
        get_yi().get_thumbnail(path),
        headers={'Cache-Control': "max-age=604800"},
        mimetype='image/jpeg')


if __name__ == "__main__":
    app.run()
    if yi is not None:
        yi.disconnect()
