from datetime import datetime, timezone
import random

from flask import url_for

from yacut import db
from .constants import (
    ASCII_LETTERS_DIGITS,
    MAX_LENGTH_LINK,
    MAX_LENGTH_CUSTOM_SHORT,
    MAX_LENGTH_RANDOM_SHORT,
    MAX_ATTEMPTS_GENERATION_SHORT,
    FORBIDDEN_SHORT_NAME,
    REDIRECT_VIEW_NAME
)

UNIQUE_SHORT_GENERATION_FAILED = (
    'Не удалось сгенерировать уникальную короткую ссылку '
    'после {attempts} попыток. Повторите попытку снова.'
)


class URLMap(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    original = db.Column(db.String(MAX_LENGTH_LINK), nullable=False)
    short = db.Column(
        db.String(MAX_LENGTH_CUSTOM_SHORT), unique=True, nullable=False
    )
    timestamp = db.Column(
        db.DateTime, index=True, default=lambda: datetime.now(timezone.utc)
    )

    def get_full_short_url(self):
        return url_for(REDIRECT_VIEW_NAME, short=self.short, _external=True)

    @classmethod
    def get(cls, short):
        return cls.query.filter_by(short=short).first()

    @classmethod
    def create(cls, original, short=None):
        if short is None:
            short = cls.generate_unique_short()
        obj = cls(original=original, short=short)
        db.session.add(obj)
        db.session.commit()
        return obj

    @classmethod
    def create_batch(cls, items):
        objects = []
        for item in items:
            obj = cls(original=item['original_link'], short=item['short'])
            objects.append(obj)
            db.session.add(obj)
        db.session.commit()
        return objects

    @classmethod
    def generate_unique_short(cls):
        for attempt in range(1, MAX_ATTEMPTS_GENERATION_SHORT + 1):
            candidate = ''.join(
                random.choices(ASCII_LETTERS_DIGITS, k=MAX_LENGTH_RANDOM_SHORT)
            )
            if candidate == FORBIDDEN_SHORT_NAME:
                continue
            if not cls.get(candidate):
                return candidate
        raise RuntimeError(
            UNIQUE_SHORT_GENERATION_FAILED.format(
                attempts=MAX_ATTEMPTS_GENERATION_SHORT
            )
        )
