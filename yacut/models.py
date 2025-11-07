from datetime import datetime, timezone
import random
import re

from flask import url_for

from yacut import db
from .constants import (
    ALLOWED_SHORT_CHARS,
    FORBIDDEN_SHORT_NAMES,
    MAX_LENGTH_LINK,
    MAX_LENGTH_SHORT,
    MAX_LENGTH_SHORT_AUTO,
    MAX_ATTEMPTS_GENERATION_SHORT,
    REGEX_PATTERN_SHORT,
    REDIRECT_VIEW_NAME
)

UNIQUE_SHORT_GENERATION_FAILED = (
    f'Не удалось сгенерировать уникальную короткую ссылку '
    f'после {MAX_ATTEMPTS_GENERATION_SHORT} попыток. Повторите попытку снова.'
)
ORIGINAL_LINK_TOO_LONG = (
    f'Оригинальная ссылка превышает {MAX_LENGTH_LINK} символов.'
)
INVALID_SHORT = 'Указано недопустимое имя для короткой ссылки'
SHORT_EXISTS = 'Предложенный вариант короткой ссылки уже существует.'


class URLMap(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    original = db.Column(db.String(MAX_LENGTH_LINK), nullable=False)
    short = db.Column(db.String(MAX_LENGTH_SHORT), unique=True, nullable=False)
    timestamp = db.Column(
        db.DateTime, index=True, default=lambda: datetime.now(timezone.utc)
    )

    def get_full_short_url(self):
        return url_for(REDIRECT_VIEW_NAME, short=self.short, _external=True)

    @staticmethod
    def get(short):
        return URLMap.query.filter_by(short=short).first()

    @staticmethod
    def create(original, short=None, validate=True):
        if validate and len(original) > MAX_LENGTH_LINK:
            raise ValueError(ORIGINAL_LINK_TOO_LONG)
        if not short:
            short = URLMap.generate_unique_short()
        else:
            if validate:
                if (
                    len(short) > MAX_LENGTH_SHORT
                    or short in FORBIDDEN_SHORT_NAMES
                    or not re.fullmatch(REGEX_PATTERN_SHORT, short)
                ):
                    raise ValueError(INVALID_SHORT)
                if URLMap.get(short):
                    raise ValueError(SHORT_EXISTS)

        url_map = URLMap(original=original, short=short)
        db.session.add(url_map)
        db.session.commit()
        return url_map

    @staticmethod
    def generate_unique_short():
        for _ in range(MAX_ATTEMPTS_GENERATION_SHORT):
            short = ''.join(
                random.choices(
                    ALLOWED_SHORT_CHARS, k=MAX_LENGTH_SHORT_AUTO
                )
            )
            if not URLMap.get(short):
                return short
        raise RuntimeError(UNIQUE_SHORT_GENERATION_FAILED)
