from math import ceil
from operator import attrgetter
import time

from flask import Flask, Response, abort, render_template, redirect, request, \
    url_for
from flask_bootstrap import Bootstrap

from . import Mode, YIDashcam, YIDashcamException, \
    YIDashcamConnectionException, YIDashcamFileException
from .config import option_map

app = Flask(__name__.split(".")[0])
Bootstrap(app)
app.config['BOOTSTRAP_SERVE_LOCAL'] = True
yi = None


class Pagination():
    """Derived from http://flask.pocoo.org/snippets/44/"""

    def __init__(self, page, per_page, total_count):
        self.page = page
        self.per_page = per_page
        self.total_count = total_count
        if page < 1 or page > self.pages:
            raise ValueError("Invalid page number")

    @property
    def pages(self):
        return ceil(self.total_count / self.per_page) or 1

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


def get_yi():
    global yi
    if yi is None:
        yi = YIDashcam(Mode.file)
    elif not yi.connected:
        yi.connect(mode=Mode.file)
    elif yi.mode != Mode.file:
        yi.set_mode(Mode.file)
    return yi


@app.errorhandler(404)
def error_404_handler(error):
    return render_template("error.html", message=error), 404


@app.errorhandler(500)
def error_500_handler(error):
    return render_template("error.html", message=error), 500


@app.errorhandler(YIDashcamException)
def yi_handler(error):
    return render_template(
        "error.html", message="Error Interfacing With YI Dashcam"), 500


@app.errorhandler(YIDashcamConnectionException)
def yi_connection_handler(error):
    return render_template(
        "error.html", message="Failed To Connect To YI Dashcam"), 500


@app.errorhandler(YIDashcamFileException)
def yi_file_handler(error):
    return render_template(
        "error.html", message="File Not Found On YI Dashcam"), 404


@app.context_processor
def yi_context():
    context = {}
    if yi is not None and yi.connected:
        context['serial_number'] = yi.serial_number
        context['firmware_version'] = yi.firmware_version
    return context


@app.route('/')
def index():
    return redirect(url_for('file_list_page', file_type="emergency"))


@app.route('/<file_type>/', defaults={'page': 1})
@app.route('/<file_type>/<int:page>')
def file_list_page(file_type, page):
    try:
        file_list = getattr(get_yi(), '{}_list'.format(file_type))
    except AttributeError:
        abort(404)
    file_list_len = len(file_list) if file_list is not None else 1
    try:
        pagination = Pagination(page, 20, file_list_len)
    except ValueError:
        # Bad page number
        abort(404)

    file_list.sort(key=attrgetter('time'), reverse=True)
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


@app.route('/delete/<path:path>', methods=["POST"])
def delete(path):
    """Delete file from dashcam"""
    path = "A:\\{}".format(path.replace('/', '\\'))
    get_yi().delete_file(path, force=True)
    return redirect(request.form.get("next", request.referrer), code=303)


@app.route('/settings', methods=["GET", "POST"])
def settings():
    """Page to interact with dashcam config"""
    if request.method == "POST":
        yi = get_yi()
        for option, cur_value in yi.config.items():
            new_value = request.form.get(option.name, None)
            if new_value is not None and int(new_value) != cur_value:
                yi.set_config(option, int(new_value))
        yi.set_mode(Mode.file)
        time.sleep(0.5)  # Allow settings to settle in
        return redirect(url_for('settings'), code=303)
    else:
        return render_template(
            'settings.html', settings=get_yi().config, option_map=option_map)
