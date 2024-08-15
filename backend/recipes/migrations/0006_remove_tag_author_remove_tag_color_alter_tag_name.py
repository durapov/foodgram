# Generated by Django 5.0.7 on 2024-08-14 20:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0005_recipe_author'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='tag',
            name='author',
        ),
        migrations.RemoveField(
            model_name='tag',
            name='color',
        ),
        migrations.AlterField(
            model_name='tag',
            name='name',
            field=models.CharField(max_length=200, unique=True, verbose_name='Название'),
        ),
    ]
