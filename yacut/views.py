from http import HTTPStatus

from flask import (
    abort, flash, render_template, redirect, send_from_directory
)

from yacut import app
from .constants import MAX_ATTEMPTS_GENERATION_SHORT
from .exceptions import YandexDiskAPIError
from .forms import URLMapForm, URLFileForm
from .models import URLMap
from .yandex_disk import async_upload_files_to_disk

FILES_SHORT_GENERATION_FAILED = (
    f'Не удалось сгенерировать уникальные короткие ссылки '
    f'после {MAX_ATTEMPTS_GENERATION_SHORT} попыток.'
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
    except (ValueError, RuntimeError) as e:
        flash(str(e))
        return render_template('index.html', form=form)

    return render_template(
        'index.html', form=form, link=url_map.get_full_short_url()
    )


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
        files_list = [
            {
                'filename': item['filename'],
                'short_link': URLMap.create(
                    original=item['original_link']
                ).get_full_short_url()
            }
            for item in destinations
        ]
    except (ValueError, RuntimeError):
        flash(FILES_SHORT_GENERATION_FAILED)
        return render_template('files.html', form=form)

    return render_template('files.html', form=form, files_list=files_list)


@app.route('/api/docs')
def openapi_spec():
    return send_from_directory('static', 'openapi.yml', mimetype='text/yaml')
