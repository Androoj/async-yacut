from flask import (
    flash, render_template, redirect, url_for, send_from_directory
)

from yacut import app, db
from .forms import URLMapForm, URLFileForm
from .models import URLMap
from .exceptions import ValidationLink
from .yandex_disk import async_upload_files_to_disk


@app.route('/', methods=('GET', 'POST'))
def index_view():
    form = URLMapForm()
    if form.validate_on_submit():
        custom_id = form.custom_id.data
        try:
            link = URLMap.create(
                original_link=form.original_link.data,
                short_link=custom_id
            )
        except ValidationLink as error:
            flash(str(error))
            return render_template('main.html', form=form)

        short_url = url_for(
            'redirect_view', short=link.short, _external=True
        )
        return render_template('main.html', form=form, link=short_url)

    return render_template('main.html', form=form)


@app.route('/<string:short>', methods=('GET',))
def redirect_view(short):
    return redirect(
        URLMap.query.filter_by(short=short).first_or_404().original
    )


@app.route('/files', methods=('GET', 'POST'))
async def files_link():
    form = URLFileForm()
    if form.validate_on_submit():
        destinations = await async_upload_files_to_disk(form.files.data)
        links = []
        if destinations:
            for file_item in destinations:
                short_link = URLMap.get_unique_short_id()
                new_item = URLMap(
                    original=file_item['original_link'],
                    short=short_link
                )
                links.append(
                    {
                        'filename': file_item['filename'],
                        'short_link': url_for(
                            'redirect_view',
                            short=short_link,
                            _external=True
                        )
                    }
                )
                db.session.add(new_item)
            db.session.commit()

        return render_template(
            'files.html',
            form=form,
            files_list=links
        )
    return render_template('files.html', form=form)


@app.route('/api/docs')
def openapi_spec():
    return send_from_directory('static', 'openapi.yml', mimetype='text/yaml')
