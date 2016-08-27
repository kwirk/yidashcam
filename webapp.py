#!/usr/bin/env python

from flask import Flask, Response, abort, render_template
import yidashcam

app = Flask(__name__)


@app.route('/')
@app.route('/emergency')
def emergency_list():
    return render_template('file_list.html', file_list=yi.emergency_list)


@app.route('/roadmap')
def roadmap_list():
    return render_template('file_list.html', file_list=yi.roadmap_list)


@app.route('/thumbnail/<path:path>')
def thumbnail(path):
    """Fetch thumbnail, and ask browser to cache for a week"""
    try:
        return Response(
            yi.get_thumbnail(path),
            headers={'Cache-Control': "max-age=604800"},
            mimetype='image/jpeg')
    except yidashcam.YIDashcamFileException:
        abort(404)


if __name__ == "__main__":
    yi = yidashcam.YIDashcam()
    yi.set_mode(yidashcam.Mode.file)
    try:
        app.run()
    finally:
        yi.disconnect()
