import json

from django.apps import apps
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from recipes.models import Ingredient


def import_data(model_name, csv_file_path):
    if model_name == 'User':
        model_class = get_user_model()
    else:
        model_class = apps.get_model(
            app_label='recipes', model_name=model_name
        )
    if model_class is None:
        raise CommandError('Модель не существует.')

    with transaction.atomic():
        with open(csv_file_path, 'r', encoding='utf-8-sig') as data:
            for row in json.load(data):
                ingredient = Ingredient(
                    name=row['name'].capitalize(),
                    measurement_unit=row['measurement_unit']
                )
                ingredient.save()


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Путь к файлу')
        parser.add_argument('model_name', type=str, help='Имя модели')

    def handle(self, *args, **options):
        file = options['csv_file']
        model = options['model_name']
        self.stdout.write(self.style.NOTICE(f'Импорт из файла {file}'))
        try:
            import_data(model, file)
        except Exception as exception:
            self.stdout.write(
                self.style.ERROR(f'Ошибка импорта:\n{exception}.'))
        else:
            self.stdout.write(self.style.SUCCESS('Импорт произведен'))
