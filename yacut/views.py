from http import HTTPStatus

from flask import (
    abort, flash, render_template, redirect, send_from_directory
)

from yacut import app
from .exceptions import YandexDiskAPIError
from .forms import URLMapForm, URLFileForm
from .models import URLMap
from .yandex_disk import async_upload_files_to_disk

FILES_SHORT_GENERATION_FAILED = (
    'Не удалось сгенерировать уникальные короткие ссылки.'
)


@app.route('/', methods=('GET', 'POST'))
def index_view():
    form = URLMapForm()
    if not form.validate_on_submit():
        return render_template('index.html', form=form)

    try:
        url_map = URLMap.create(
            original=form.original_link.data,
            short=form.custom_id.data or None
        )
        short_url = url_map.get_full_short_url()
    except (ValueError, RuntimeError) as e:
        flash(str(e))
        return render_template('index.html', form=form)

    return render_template('index.html', form=form, link=short_url)


@app.route('/<string:short>', methods=('GET',))
def redirect_view(short):
    if (url_map := URLMap.get(short)) is None:
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
        files_list = []
        for item in destinations:
            url_map = URLMap.create(original=item['original_link'], short=None)
            files_list.append({
                'filename': item['filename'],
                'short_link': url_map.get_full_short_url()
            })
    except RuntimeError:
        flash(FILES_SHORT_GENERATION_FAILED)
        return render_template('files.html', form=form)

    return render_template('files.html', form=form, files_list=files_list)


@app.route('/api/docs')
def openapi_spec():
    return send_from_directory('static', 'openapi.yml', mimetype='text/yaml')
