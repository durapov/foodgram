from datetime import timezone

from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser, PermissionsMixin
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.validators import RegexValidator, MinValueValidator
from django.db import models

from backend.constants import MAX_NAME_LENGTH, MAX_EMAIL_LENGTH
######
from django.contrib import admin
from django.contrib.auth.models import AbstractUser
from django.core.validators import (MaxValueValidator, MinValueValidator,
                                    RegexValidator)
from django.db import models

STRING_LENGTH = 20

class User(AbstractUser):

    ROLES = (('admin', 'Администратор'), ('moderator', 'Модератор'),
             ('user', 'Пользователь'),)
    REQUIRED_FIELDS = ('username', 'last_name', 'first_name',)
    USERNAME_FIELD = 'email'

    email = models.EmailField(
        verbose_name='Адрес электронной почты',
        max_length=MAX_EMAIL_LENGTH,
        unique=True,
    )
    username = models.CharField(
        verbose_name='Уникальный юзернэйм',
        max_length=MAX_NAME_LENGTH,
        validators=[UnicodeUsernameValidator()],
        unique=True,
        error_messages={
            'unique': 'Пользователь с таким именем уже существует.',
        }
    )
    first_name = models.CharField(
        verbose_name='Имя',
        max_length=MAX_NAME_LENGTH,
    )
    last_name = models.CharField(
        verbose_name='Фамилия',
        max_length=MAX_NAME_LENGTH,
    )
    role = models.CharField(max_length=30, verbose_name='роль',
                            choices=ROLES, default='user')

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('id',)

    def __str__(self):
        return self.username

    @property
    def is_admin(self):
        return self.role == 'admin' or self.is_superuser or self.is_staff

    @property
    def is_moderator(self):
        return self.role == 'moderator'


class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'role')
    search_fields = ('username', 'email', 'role')
    list_filter = ('role',)



class Recipe(models.Model):
    tags = models.ManyToManyField('Tag')
    #     'Tag',
    #     through='TagsInRecipe',
    #     related_name='tags'
    # )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipe_author',
        null=True, blank=True
    )
    ingredients = models.ManyToManyField(
        'Ingredient',
        through='IngredientInRecipe',
        related_name='ingredients'
    )
    is_favorited = models.BooleanField('Находится ли в избранном')
    is_in_shopping_cart = models.BooleanField('Находится ли в корзине')
    name = models.CharField('Название', max_length=200)
    image = models.URLField('Ссылка на картинку на сайте')
    text = models.TextField('Описание')
    # cooking_time = models.PositiveSmallIntegerField(
    #     'Время приготовления (в минутах)',
    #     validators=[MinValueValidator(1)]
    # ),
    pub_date = models.DateTimeField('Дата публикации', auto_now_add=True
    )
    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ['pub_date']


class Tag(models.Model):
    name = models.CharField('Название', max_length=200)
    color = models.CharField('Цвет в HEX', max_length=7)
    slug = models.CharField(
        'Уникальный слаг', max_length=200,
        unique=True,
        null=True, blank=True,
        validators=[RegexValidator(
            regex=r'^[-a-zA-Z0-9_]+$',
            message='Неподходящий слаг')
        ]
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='tag_author',
        null=True, blank=True
    )

    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'
        ordering = ['name']


class Ingredient(models.Model):
    name = models.CharField('Название', max_length=200)
    measurment_unit = models.CharField('Единицы измерения', max_length=200)

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ['name']


class IngredientInRecipe(models.Model):
    name = models.ForeignKey(
        Ingredient,
        related_name='IngredientInRecipe',
        on_delete=models.CASCADE,
        verbose_name='Ингредиент'
    )
    recipe = models.ForeignKey(
        Recipe,
        related_name='recipe',
        on_delete=models.CASCADE,
        verbose_name='Рецепт'
    )
    amount = models.PositiveSmallIntegerField(
         verbose_name='Количество ингредиента',
         validators=[MinValueValidator(1)]
    )

    class Meta:
        verbose_name = 'Список ингредиентов рецепта'
        verbose_name_plural = 'Списки ингредиентов рецептов'

class ShopingCart(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        related_name='recipe_in_cart',
        on_delete=models.CASCADE,
        verbose_name='Рецепт'
    )
    user = models.ForeignKey(
        User,
        related_name='user_in_cart',
        on_delete=models.CASCADE,
        verbose_name='Пользователь'
    )

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'


class Subscription(models.Model):
    class Meta:
        verbose_name = 'Подписка на пользователя'
        verbose_name_plural = 'Подписки на пользователей'

class Favorite(models.Model):
    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'

