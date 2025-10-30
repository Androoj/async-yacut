from http import HTTPStatus

from flask import jsonify, request, url_for

from yacut import app
from .error_handlers import InvalidAPIUsage
from .models import URLMap
from .exceptions import ValidationLink


@app.route('/api/id/', methods=('POST',))
def create_new_short_link():
    if not request.is_json:
        raise InvalidAPIUsage('Отсутствует тело запроса')
    data = request.get_json(silent=True)
    if data is None:
        raise InvalidAPIUsage('Отсутствует тело запроса')
    url = data.get('url')
    custom_id = data.get('custom_id')
    if url is None:
        raise InvalidAPIUsage('\"url\" является обязательным полем!')
    try:
        object_model = URLMap.create(original_link=url, short_link=custom_id)
        short_link_url = url_for(
            'redirect_view', short=object_model.short, _external=True
        )
        return jsonify({
            'url': object_model.original,
            'short_link': short_link_url
        }), HTTPStatus.CREATED
    except ValidationLink as error:
        raise InvalidAPIUsage(str(error))


@app.route('/api/id/<string:short_id>/', methods=('GET',))
def get_short_link(short_id):
    link = URLMap.get(short_id)
    if link is None:
        raise InvalidAPIUsage('Указанный id не найден', HTTPStatus.NOT_FOUND)
    return jsonify({'url': link.original}), HTTPStatus.OK
