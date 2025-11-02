import re

from http import HTTPStatus
from flask import jsonify, request

from yacut import app
from .error_handlers import InvalidAPIUsage
from .models import URLMap
from .exceptions import ValidationLink
from .constants import (
    MAX_LENGTH_CUSTOM_SHORT,
    REGEX_PATTERN_SHORT_NAME,
    FORBIDDEN_SHORT_NAME
)

REQUEST_BODY_MISSING = 'Отсутствует тело запроса'
URL_REQUIRED = '"url" является обязательным полем!'
INVALID_SHORT = 'Указано недопустимое имя для короткой ссылки'
SHORT_EXISTS = 'Предложенный вариант короткой ссылки уже существует.'
SHORT_NOT_FOUND = 'Указанный id не найден'


def validate_custom_id(short):
    if not short:
        return None
    if len(short) > MAX_LENGTH_CUSTOM_SHORT:
        raise InvalidAPIUsage(INVALID_SHORT, HTTPStatus.BAD_REQUEST)
    if short == FORBIDDEN_SHORT_NAME:
        raise InvalidAPIUsage(SHORT_EXISTS, HTTPStatus.BAD_REQUEST)
    if not re.fullmatch(REGEX_PATTERN_SHORT_NAME, short):
        raise InvalidAPIUsage(INVALID_SHORT, HTTPStatus.BAD_REQUEST)
    if URLMap.get(short):
        raise InvalidAPIUsage(SHORT_EXISTS, HTTPStatus.BAD_REQUEST)
    return short


@app.route('/api/id/', methods=('POST',))
def create_new_short_link():
    if not request.is_json:
        raise InvalidAPIUsage(REQUEST_BODY_MISSING)
    data = request.get_json(silent=True)
    if data is None:
        raise InvalidAPIUsage(REQUEST_BODY_MISSING)
    if 'url' not in data:
        raise InvalidAPIUsage(URL_REQUIRED, HTTPStatus.BAD_REQUEST)

    url = data['url']
    custom_id = data.get('custom_id')
    short = validate_custom_id(custom_id) if custom_id else None

    try:
        obj = URLMap.create(original=url, short=short)
        short_url = obj.get_full_short_url()
        return jsonify({
            'url': obj.original,
            'short_link': short_url
        }), HTTPStatus.CREATED
    except ValidationLink as error:
        raise InvalidAPIUsage(str(error), HTTPStatus.INTERNAL_SERVER_ERROR)


@app.route('/api/id/<string:short>/', methods=('GET',))
def get_short_link(short):
    url_map = URLMap.get(short)
    if url_map is None:
        raise InvalidAPIUsage(SHORT_NOT_FOUND, HTTPStatus.NOT_FOUND)
    return jsonify({'url': url_map.original}), HTTPStatus.OK
