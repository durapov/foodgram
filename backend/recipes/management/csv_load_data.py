import csv

from django.apps import apps
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db import models, transaction


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
        with open(csv_file_path, 'r', encoding='utf-8-sig') as csvfile:
            file_data = csv.DictReader(csvfile)
            for item in file_data:
                data = model_class(**item)
                for field_name, value in item.items():
                    if hasattr(data, field_name) and isinstance(
                            getattr(data, field_name), models.ForeignKey):
                        related_model = apps.get_model(
                            app_label='recipes',
                            model_name=data._meta.get_field(
                                field_name
                            ).related_model
                        )
                        related_object = related_model.objects.get(pk=value)
                        setattr(data, field_name, related_object)
                data.full_clean()
                data.save()


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
