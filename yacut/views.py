from http import HTTPStatus
from flask import (
    abort, flash, render_template, redirect, send_from_directory
)

from yacut import app
from .exceptions import YandexDiskAPIError
from .forms import URLMapForm, URLFileForm
from .models import URLMap
from .yandex_disk import async_upload_files_to_disk


@app.route('/', methods=('GET', 'POST'))
def index_view():
    form = URLMapForm()
    if not form.validate_on_submit():
        return render_template('main.html', form=form)

    short = form.custom_id.data or None

    try:
        obj = URLMap.create(original=form.original_link.data, short=short)
        short_url = obj.get_full_short_url()
    except RuntimeError as e:
        flash(str(e))
        return render_template('main.html', form=form)

    return render_template('main.html', form=form, link=short_url)


@app.route('/<string:short>', methods=('GET',))
def redirect_view(short):
    url_map = URLMap.get(short)
    if url_map is None:
        abort(HTTPStatus.NOT_FOUND)
    return redirect(url_map.original)


@app.route('/files', methods=('GET', 'POST'))
async def files_link():
    form = URLFileForm()
    if not form.validate_on_submit():
        return render_template('files.html', form=form)

    try:
        destinations = await async_upload_files_to_disk(form.files.data)
    except YandexDiskAPIError as e:
        flash(str(e))
        return render_template('files.html', form=form)

    try:
        file_items = [
            {
                'original_link': item['original_link'],
                'short': URLMap.generate_unique_short()
            }
            for item in destinations
        ]
        URLMap.create_batch(file_items)

        files_list = [
            {
                'filename': item['filename'],
                'short_link': URLMap(
                    original=item['original_link'],
                    short=file_items[i]['short']
                ).get_full_short_url()
            }
            for i, item in enumerate(destinations)
        ]
    except RuntimeError:
        flash('Не удалось сгенерировать уникальные короткие ссылки.')
        return render_template('files.html', form=form)

    return render_template('files.html', form=form, files_list=files_list)


@app.route('/api/docs')
def openapi_spec():
    return send_from_directory('static', 'openapi.yml', mimetype='text/yaml')
