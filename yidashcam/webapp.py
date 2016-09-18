#!/usr/bin/env python

from math import ceil
import time

from flask import Flask, Response, abort, render_template, request, url_for

import yidashcam

app = Flask(__name__)
yi = None


class Pagination(object):
    """Derived from http://flask.pocoo.org/snippets/44/"""

    def __init__(self, page, per_page, total_count):
        self.page = page
        self.per_page = per_page
        self.total_count = total_count
        if page < 1 or page > self.pages:
            raise ValueError("Invalid page number")

    @property
    def pages(self):
        return ceil(self.total_count / self.per_page)

    @property
    def has_prev(self):
        return self.page > 1

    @property
    def has_next(self):
        return self.page < self.pages

    @property
    def first_item_index(self):
        return (self.page - 1) * self.per_page

    @property
    def last_item_index(self):
        if self.page == self.pages:
            return self.total_count
        else:
            return self.page * self.per_page

    def page_items(self, items):
        """Return list of items on current page from `items`"""
        return items[self.first_item_index:self.last_item_index]


def url_for_other_page(page):
    """http://flask.pocoo.org/snippets/44/"""
    args = request.view_args.copy()
    args['page'] = page
    return url_for(request.endpoint, **args)


app.jinja_env.globals['url_for_other_page'] = url_for_other_page


@app.before_first_request
def connect_yi():
    global yi
    if yi is None:
        yi = yidashcam.YIDashcam(mode=yidashcam.Mode.file)
    elif yi.mode != yidashcam.Mode.file:
        yi.set_mode(yidashcam.Mode.file)


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


@app.route('/', defaults={'file_type': 'emergency', 'page': 1})
@app.route('/<file_type>/', defaults={'page': 1})
@app.route('/<file_type>/<int:page>')
def file_list_page(file_type, page):
    try:
        file_list = getattr(get_yi(), '{}_list'.format(file_type), None)
    except AttributeError:
        abort(404)
    try:
        pagination = Pagination(page, 20, len(file_list))
    except ValueError:
        # Bad page number
        abort(404)

    file_list.sort(reverse=True)
    return render_template(
        'file_list.html',
        file_type=file_type,
        file_list=pagination.page_items(file_list),
        pagination=pagination)


@app.route('/thumbnail/<path:path>')
def thumbnail(path):
    """Fetch thumbnail, and ask browser to cache for a week"""
    return Response(
        get_yi().get_thumbnail(path),
        headers={'Cache-Control': "max-age=604800"},
        mimetype='image/jpeg')


@app.route('/config', methods=["GET", "POST"])
def config():
    """Page to interact with dashcam config"""
    if request.method == "POST":
        cur_config = get_yi().config
        for option, type_ in yidashcam.config.option_map.items():
            if type_ is str:
                continue
            value = int(request.form.get(option.name, 0))
            if value != cur_config[option]:
                get_yi().set_config(option, value)
        get_yi().set_mode(yidashcam.Mode.file)
        time.sleep(0.5) # Allow settings to settle in
    return render_template(
        'config.html',
        config=get_yi().config,
        option_map=yidashcam.config.option_map)
