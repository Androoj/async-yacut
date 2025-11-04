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
    MAX_LENGTH_SHORT,
    REGEX_PATTERN_SHORT,
    FORBIDDEN_SHORT_NAME
)
from .models import URLMap

LABEL_ORIGINAL_LINK = 'Оригинальная ссылка'
LABEL_SHORT = 'Ваш вариант короткой ссылки'
ORIGINAL_LINK_TOO_LONG = (
    f'Ссылка не должна превышать {MAX_LENGTH_LINK} символов.'
)
ORIGINAL_LINK_REQUIRED = 'Обязательное поле'
SHORT_INVALID_CHARS = (
    'Допустимы символы латинского алфавита и цифры от 0 до 9.'
)
SHORT_UNAVAILABLE = 'Предложенный вариант короткой ссылки уже существует.'
SUBMIT_BUTTON_TEXT = 'Создать'
UPLOAD_BUTTON_TEXT = 'Загрузить'


class URLMapForm(FlaskForm):
    original_link = URLField(
        LABEL_ORIGINAL_LINK,
        validators=(
            DataRequired(message=ORIGINAL_LINK_REQUIRED),
            Length(max=MAX_LENGTH_LINK, message=ORIGINAL_LINK_TOO_LONG),
        )
    )
    custom_id = StringField(
        LABEL_SHORT,
        validators=(
            Optional(),
            Length(max=MAX_LENGTH_SHORT),
            Regexp(REGEX_PATTERN_SHORT, message=SHORT_INVALID_CHARS)
        )
    )
    submit = SubmitField(SUBMIT_BUTTON_TEXT)

    def validate_custom_id(self, field):
        if field.data in FORBIDDEN_SHORT_NAME:
            raise ValidationError(SHORT_UNAVAILABLE)
        if URLMap.get(field.data) is not None:
            raise ValidationError(SHORT_UNAVAILABLE)


class URLFileForm(FlaskForm):
    files = MultipleFileField(validators=(DataRequired(),))
    submit = SubmitField(UPLOAD_BUTTON_TEXT)
