from http import HTTPStatus
import re

from flask import jsonify, request

from yacut import app
from .constants import (
    FORBIDDEN_SHORT_NAMES,
    MAX_LENGTH_LINK,
    MAX_LENGTH_SHORT,
    REGEX_PATTERN_SHORT
)
from .error_handlers import InvalidAPIUsage
from .models import URLMap

REQUEST_BODY_MISSING = 'Отсутствует тело запроса'
URL_REQUIRED = '"url" является обязательным полем!'
ORIGINAL_LINK_TOO_LONG = f'Оригинальная ссылка превышает {MAX_LENGTH_LINK} символов.'
INVALID_SHORT = 'Указано недопустимое имя для короткой ссылки'
SHORT_EXISTS = 'Предложенный вариант короткой ссылки уже существует.'
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
    
    if len(data['url']) > MAX_LENGTH_LINK:
        raise InvalidAPIUsage(ORIGINAL_LINK_TOO_LONG)
    
    short = data.get('custom_id')

    if not short:
        short = None
    
    if short is not None:
        if len(short) > MAX_LENGTH_SHORT:
            raise InvalidAPIUsage(INVALID_SHORT)
        if short in FORBIDDEN_SHORT_NAMES:
            raise InvalidAPIUsage(INVALID_SHORT)
        if not re.fullmatch(REGEX_PATTERN_SHORT, short):
            raise InvalidAPIUsage(INVALID_SHORT)
        if URLMap.get(short) is not None:
            raise InvalidAPIUsage(SHORT_EXISTS)

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
        raise InvalidAPIUsage(SHORT_NOT_FOUND, HTTPStatus.NOT_FOUND)
    return jsonify({'url': url_map.original}), HTTPStatus.OK
