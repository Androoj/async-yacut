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
    MAX_LENGTH_LINK,
    MAX_LENGTH_CUSTOM_SHORT,
    REGEX_PATTERN_SHORT_NAME,
    FORBIDDEN_SHORT_NAME
)
from .models import URLMap

ORIGINAL_LINK_TOO_LONG = 'Ссылка не должна превышать 2048 символов.'
ORIGINAL_LINK_REQUIRED = 'Обязательное поле'
CUSTOM_ID_INVALID_CHARS = (
    'Допустимы символы латинского алфавита и цифры от 0 до 9.'
)
CUSTOM_ID_UNAVAILABLE = 'Предложенный вариант короткой ссылки уже существует.'
SUBMIT_BUTTON_TEXT = 'Создать'
UPLOAD_BUTTON_TEXT = 'Загрузить'


class URLMapForm(FlaskForm):
    original_link = URLField(
        'Оригинальная ссылка',
        validators=(
            DataRequired(message=ORIGINAL_LINK_REQUIRED),
            Length(max=MAX_LENGTH_LINK, message=ORIGINAL_LINK_TOO_LONG),
        )
    )
    custom_id = StringField(
        'Ваш вариант короткой ссылки',
        validators=(
            Optional(),
            Length(min=1, max=MAX_LENGTH_CUSTOM_SHORT),
            Regexp(
                REGEX_PATTERN_SHORT_NAME,
                message=CUSTOM_ID_INVALID_CHARS
            )
        )
    )
    submit = SubmitField(SUBMIT_BUTTON_TEXT)

    def validate_custom_id(self, field):
        if field.data == FORBIDDEN_SHORT_NAME or URLMap.get(field.data):
            raise ValidationError(CUSTOM_ID_UNAVAILABLE)


class URLFileForm(FlaskForm):
    files = MultipleFileField(validators=(DataRequired(),))
    submit = SubmitField(UPLOAD_BUTTON_TEXT)
