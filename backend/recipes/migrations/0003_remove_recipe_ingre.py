# Generated by Django 5.0.7 on 2024-09-26 19:02

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0002_recipe_ingre'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='recipe',
            name='ingre',
        ),
    ]
