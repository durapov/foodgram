# import base64
#
# from django.core.files.base import ContentFile
# from rest_framework import serializers
#
#
# class Base64ImageField(serializers.ImageField):
#     def to_internal_value(self, data):
#         # Если полученный объект строка, и эта строка
#         # начинается с 'data:image'...
#         if isinstance(data, str) and data.startswith('data:image'):
#             # ...начинаем декодировать изображение из base64.
#             # Сначала нужно разделить строку на части.
#             format_str, img_str = data.split(';base64,')
#             # И извлечь расширение файла.
#             ext = format_str.split('/')[-1]
#             # Затем декодировать сами данные и поместить результат в файл,
#             # которому дать название по шаблону.
#             data = ContentFile(base64.b64decode(img_str), name='temp.' + ext)
#             print('====1', data.__dict__)
#             print('====2', super().to_internal_value(data))
#
#         return super().to_internal_value(data)
