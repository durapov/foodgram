from django.core.validators import RegexValidator

username_validator = RegexValidator(
    regex=r'^[\w.@+-]=\Z',
    message='Неверный формат имени пользователя',
    code='invalid_username'
)