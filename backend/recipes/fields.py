import base64
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from rest_framework import fields


class Base64ImageField(fields.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str):
            if data.startswith('data:image/'):
                format, imgstr = data.split(';base64,')
                ext = format.split('/')[-1]
                file = ContentFile(base64.b64decode(imgstr),
                                   name=f'temp.{ext}')
                return super().to_internal_value(file)
            else:
                raise ValidationError(
                    'Неверный формат изображения. Ожидается base64 строка.')
        return super().to_internal_value(data)
