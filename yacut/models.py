from datetime import datetime, timezone
import random
import re

from yacut import db
from .constants import (
    MIN_LENGHT_ALL_LINK,
    MAX_LENGHT_CUSTOM_LINK,
    ASCII_LETTERS_DIGITS,
    MAX_LENGHT_RANDOM_LINK,
    MAX_ATTEMPTS_GENERATION_LINK,
    FORBIDDEN_LINK_NAME,
    REGEX_PATTERN_LINK_NAME
)
from .exceptions import ValidationLink


class URLMap(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    original = db.Column(db.String, nullable=False)
    short = db.Column(
        db.String(MAX_LENGHT_CUSTOM_LINK), unique=True, nullable=False
    )
    timestamp = db.Column(
        db.DateTime, index=True, default=datetime.now(timezone.utc)
    )

    def from_dict(self, data):
        setattr(self, 'original', data['url'])
        setattr(self, 'short', data['custom_id'])

    def to_dict(self):
        return {
            'url': self.original,
            'short': self.short
        }

    @staticmethod
    def generate_short_link():
        return ''.join(
            random.choices(
                ASCII_LETTERS_DIGITS,
                k=MAX_LENGHT_RANDOM_LINK
            )
        )

    @classmethod
    def get_unique_short_id(cls):
        for _ in range(MAX_ATTEMPTS_GENERATION_LINK):
            short = cls.generate_short_link()
            if not URLMap.get(short):
                return short
        raise ValidationLink(
            'Не удалось сгенерировать уникальную короткую ссылку. '
            'Повторите попытку снова.'
        )

    @staticmethod
    def get(short_link):
        return URLMap.query.filter_by(short=short_link).first()

    @staticmethod
    def create(original_link, short_link=None):
        if short_link:
            if (
                len(short_link) > MAX_LENGHT_CUSTOM_LINK
                or len(short_link) < MIN_LENGHT_ALL_LINK
                or short_link == FORBIDDEN_LINK_NAME
                or not bool(re.match(REGEX_PATTERN_LINK_NAME, short_link))
            ):
                raise ValidationLink(
                    'Указано недопустимое имя для короткой ссылки'
                )
            if URLMap.get(short_link):
                raise ValidationLink(
                    'Предложенный вариант короткой ссылки уже существует.'
                )
        else:
            short_link = URLMap.get_unique_short_id()
        object_model = URLMap(original=original_link, short=short_link)
        db.session.add(object_model)
        db.session.commit()
        return object_model
