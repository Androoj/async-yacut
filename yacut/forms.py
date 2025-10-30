from flask_wtf import FlaskForm
from flask_wtf.file import MultipleFileField
from wtforms import StringField, SubmitField, URLField
from wtforms.validators import (
    DataRequired,
    Length,
    Optional,
    Regexp,
    ValidationError
)

from .constants import (
    MIN_LENGHT_ALL_LINK,
    MAX_LENGHT_CUSTOM_LINK,
    REGEX_PATTERN_LINK_NAME,
    FORBIDDEN_LINK_NAME
)

from .models import URLMap


class URLMapForm(FlaskForm):
    original_link = URLField(
        'Оригинальная ссылка',
        validators=(
            DataRequired(message='Обязательное поле'),
        )
    )
    custom_id = StringField(
        'Ваш вариант короткой ссылки',
        validators=(
            Optional(),
            Length(MIN_LENGHT_ALL_LINK, MAX_LENGHT_CUSTOM_LINK),
            Regexp(
                REGEX_PATTERN_LINK_NAME,
                message='Допустимы символы латинского '
                        'алфавита и цифры от 0 до 9.'
            )
        )
    )
    submit = SubmitField('Создать')

    def validate_custom_id(self, field):
        if URLMap.get(field.data):
            raise ValidationError(
                'Предложенный вариант короткой ссылки уже существует.'
            )
        if field.data == FORBIDDEN_LINK_NAME:
            raise ValidationError(
                'Предложенный вариант короткой ссылки уже существует.'
            )


class URLFileForm(FlaskForm):
    files = MultipleFileField(validators=(DataRequired(),))
    submit = SubmitField('Загрузить')