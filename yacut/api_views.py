from http import HTTPStatus

from flask import jsonify, request

from yacut import app
from .error_handlers import InvalidAPIUsage
from .models import URLMap

REQUEST_BODY_MISSING = 'Отсутствует тело запроса'
URL_REQUIRED = '"url" является обязательным полем!'
SHORT_NOT_FOUND = 'Указанный id не найден'


@app.route('/api/id/', methods=('POST',))
def create_new_short():
    if not request.is_json:
        raise InvalidAPIUsage(REQUEST_BODY_MISSING)
    data = request.get_json(silent=True)
    if data is None:
        raise InvalidAPIUsage(REQUEST_BODY_MISSING)
    if 'url' not in data:
        raise InvalidAPIUsage(URL_REQUIRED)

    try:
        return jsonify({
            'url': data['url'],
            'short_link': URLMap.create(
                original=data['url'], short=data.get('custom_id')
            ).get_full_short_url()
        }), HTTPStatus.CREATED
    except (ValueError, RuntimeError) as e:
        raise InvalidAPIUsage(str(e))


@app.route('/api/id/<string:short>/', methods=('GET',))
def get_original_url(short):
    if not (url_map := URLMap.get(short)):
        raise InvalidAPIUsage('Указанный id не найден', HTTPStatus.NOT_FOUND)
    return jsonify({'url': url_map.original}), HTTPStatus.OK
