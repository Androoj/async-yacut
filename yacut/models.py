from datetime import datetime, timezone
import random
import re

from flask import url_for

from yacut import db
from .constants import (
    SHORT_CODE_ALPHABET,
    MAX_LENGTH_LINK,
    MAX_LENGTH_SHORT,
    MAX_LENGTH_SHORT_AUTO,
    MAX_ATTEMPTS_GENERATION_SHORT,
    FORBIDDEN_SHORT_NAME,
    REGEX_PATTERN_SHORT,
    REDIRECT_VIEW_NAME
)

UNIQUE_SHORT_GENERATION_FAILED = (
    f'Не удалось сгенерировать уникальную короткую ссылку '
    f'после {MAX_ATTEMPTS_GENERATION_SHORT} попыток. Повторите попытку снова.'
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
    def validate_short(short):
        if not short:
            raise ValueError(INVALID_SHORT)

        if len(short) > MAX_LENGTH_SHORT:
            raise ValueError(INVALID_SHORT)

        if short in FORBIDDEN_SHORT_NAME:
            raise ValueError(INVALID_SHORT)

        if not re.fullmatch(REGEX_PATTERN_SHORT, short):
            raise ValueError(INVALID_SHORT)

        if URLMap.get(short) is not None:
            raise ValueError(SHORT_EXISTS)

    @staticmethod
    def create(original, short=None):
        if short == "":
            short = None

        if short is not None:
            URLMap.validate_short(short)
        else:
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
                random.choices(SHORT_CODE_ALPHABET, k=MAX_LENGTH_SHORT_AUTO)
            )
            if short in FORBIDDEN_SHORT_NAME or not pattern.fullmatch(short):
                continue
            if URLMap.get(short) is None:
                return short
        raise RuntimeError(UNIQUE_SHORT_GENERATION_FAILED)
