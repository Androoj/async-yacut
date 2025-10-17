from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, URLField
from wtforms.validators import DataRequired, Length, Optional

from constants import (
    MIN_LENGHT_LINK, MAX_LENGHT_LINK, MAX_LENGHT_CUSTOM_LINK
)


class URLMapForm(FlaskForm):
    original_link = URLField(
        'Оригинальная ссылка',
        validators=(
            DataRequired(message='Обязательное поле'),
            Length(MIN_LENGHT_LINK, MAX_LENGHT_LINK)
        )
    )
    custom_id = StringField(
        'Ваш вариант короткой ссылки',
        validators=(
            Length(MIN_LENGHT_LINK, MAX_LENGHT_CUSTOM_LINK),
            Optional()
        )
    )
    submit = SubmitField('Создать')