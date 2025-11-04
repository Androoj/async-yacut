from http import HTTPStatus

from flask import jsonify, request

from yacut import app
from .error_handlers import InvalidAPIUsage
from .models import (
    URLMap,
    ERROR_SHORT_INVALID_CHARS,
    ERROR_SHORT_TOO_LONG,
    ERROR_SHORT_FORBIDDEN,
    ERROR_SHORT_EMPTY,
    ERROR_SHORT_NOT_UNIQUE
)

REQUEST_BODY_MISSING = 'Отсутствует тело запроса'
URL_REQUIRED = '"url" является обязательным полем!'
SHORT_NOT_FOUND = 'Указанный id не найден'
INVALID_SHORT = 'Указано недопустимое имя для короткой ссылки'
SHORT_EXISTS = 'Предложенный вариант короткой ссылки уже существует.'


@app.route('/api/id/', methods=('POST',))
def create_new_short_link():
    if not request.is_json:
        raise InvalidAPIUsage(REQUEST_BODY_MISSING)
    data = request.get_json(silent=True)
    if data is None:
        raise InvalidAPIUsage(REQUEST_BODY_MISSING)
    if 'url' not in data:
        raise InvalidAPIUsage(URL_REQUIRED, HTTPStatus.BAD_REQUEST)

    custom_id = data.get('custom_id')
    if custom_id == "":
        custom_id = None

    try:
        url_map = URLMap.create(original=data['url'], short=custom_id)
    except ValueError as e:
        if str(e) in (
            ERROR_SHORT_INVALID_CHARS,
            ERROR_SHORT_TOO_LONG,
            ERROR_SHORT_FORBIDDEN,
            ERROR_SHORT_EMPTY
        ):
            raise InvalidAPIUsage(INVALID_SHORT, HTTPStatus.BAD_REQUEST)
        elif str(e) == ERROR_SHORT_NOT_UNIQUE:
            raise InvalidAPIUsage(SHORT_EXISTS, HTTPStatus.BAD_REQUEST)
        else:
            raise InvalidAPIUsage(str(e), HTTPStatus.BAD_REQUEST)

    return jsonify({
        'url': data['url'],
        'short_link': url_map.get_full_short_url()
    }), HTTPStatus.CREATED


@app.route('/api/id/<string:short>/', methods=('GET',))
def get_short_link(short):
    if (url_map := URLMap.get(short)) is None:
        raise InvalidAPIUsage(SHORT_NOT_FOUND, HTTPStatus.NOT_FOUND)
    return jsonify({'url': url_map.original}), HTTPStatus.OK
