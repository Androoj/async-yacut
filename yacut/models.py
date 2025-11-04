from datetime import datetime, timezone
import random
import re

from flask import url_for

from yacut import db
from .constants import (
    LETTERS_DIGITS,
    MAX_LENGTH_LINK,
    MAX_LENGTH_SHORT,
    MAX_LENGTH_SHORT_AUTO,
    MAX_ATTEMPTS_GENERATION_SHORT,
    FORBIDDEN_SHORT_NAME,
    REGEX_PATTERN_SHORT,
    REDIRECT_VIEW_NAME
)

ERROR_ORIGINAL_EMPTY = 'Укажите оригинальную ссылку.'
ERROR_ORIGINAL_TOO_LONG = (
    f'Слишком длинная ссылка. Максимальная длина — '
    f'{MAX_LENGTH_LINK} символов.'
)
ERROR_SHORT_EMPTY = 'Укажите короткий идентификатор.'
ERROR_SHORT_TOO_LONG = (
    f'Слишком длинный идентификатор. Максимальная длина — '
    f'{MAX_LENGTH_SHORT} символов.'
)
ERROR_SHORT_FORBIDDEN = 'Указанное имя запрещено.'
ERROR_SHORT_INVALID_CHARS = (
    'Идентификатор может содержать только латинские буквы и цифры.'
)
ERROR_SHORT_NOT_UNIQUE = 'Идентификатор уже занят.'

UNIQUE_SHORT_GENERATION_FAILED = (
    f'Не удалось сгенерировать уникальную короткую ссылку '
    f'после {MAX_ATTEMPTS_GENERATION_SHORT} попыток. Повторите попытку снова.'
)


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
    def create(original, short=None):
        if not original:
            raise ValueError(ERROR_ORIGINAL_EMPTY)
        if len(original) > MAX_LENGTH_LINK:
            raise ValueError(ERROR_ORIGINAL_TOO_LONG)

        if short is not None:
            if not short:
                raise ValueError(ERROR_SHORT_EMPTY)
            if len(short) > MAX_LENGTH_SHORT:
                raise ValueError(ERROR_SHORT_TOO_LONG)
            if short in FORBIDDEN_SHORT_NAME:
                raise ValueError(ERROR_SHORT_FORBIDDEN)
            if not re.fullmatch(REGEX_PATTERN_SHORT, short):
                raise ValueError(ERROR_SHORT_INVALID_CHARS)
            if URLMap.get(short) is not None:
                raise ValueError(ERROR_SHORT_NOT_UNIQUE)

        if short is None:
            short = URLMap.generate_unique_short()

        url_map = URLMap(original=original, short=short)
        db.session.add(url_map)
        db.session.commit()
        return url_map

    @staticmethod
    def generate_unique_short():
        pattern = re.compile(REGEX_PATTERN_SHORT)
        for _ in range(MAX_ATTEMPTS_GENERATION_SHORT):
            short = ''.join(
                random.choices(LETTERS_DIGITS, k=MAX_LENGTH_SHORT_AUTO)
            )
            if short in FORBIDDEN_SHORT_NAME or not pattern.fullmatch(short):
                continue
            if URLMap.get(short) is None:
                return short
        raise RuntimeError(UNIQUE_SHORT_GENERATION_FAILED)
