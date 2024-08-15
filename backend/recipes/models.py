import datetime
from datetime import timezone
from django.core.exceptions import BadRequest
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

class ApiUser(AbstractUser):

    ROLES = (('admin', 'Администратор'), ('moderator', 'Модератор'),
             ('user', 'Пользователь'),)
    REQUIRED_FIELDS = ('username', 'first_name', 'last_name',)
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
    is_subscribed = models.BooleanField(
        verbose_name='Подписка на пользователя',
        default = False

    )
    avatar = models.URLField(
        verbose_name='Аватар',
    )


    role = models.CharField(max_length=30, verbose_name='роль',
                            choices=ROLES, default='user')

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('id',)
        # fields = ('email', 'id', 'username', 'first_name', 'lastname', 'is_subscribed', 'avatar')

    def __str__(self):
        return self.username

    @property
    def is_admin(self):
        return self.role == 'admin' or self.is_superuser or self.is_staff

    @property
    def is_moderator(self):
        return self.role == 'moderator'


class Tag(models.Model):
    name = models.CharField('Название', unique=True, max_length=200)
    slug = models.CharField(
        'Уникальный слаг', max_length=200,
        unique=True,
        null=True, blank=True,
        validators=[RegexValidator(
            regex=r'^[-a-zA-Z0-9_]+$',
            message='Неподходящий слаг')
        ]
    )

    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'
        ordering = ['name']

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField('Название', max_length=128)
    measurement_unit = models.CharField(
        'Единицы измерения',
        max_length=64,
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ['name']

    def __str__(self):
        return self.name



class Recipe(models.Model):
    name = models.CharField('Название', max_length=200)
    text = models.TextField('Описание')
    cooking_time = models.PositiveSmallIntegerField(
         'Время приготовления (в минутах)',
         validators=[MinValueValidator(1)]
    )
    image = models.URLField('Ссылка на картинку на сайте')
    # is_favorited = models.BooleanField('Находится ли в избранном')
    # is_in_shopping_cart = models.BooleanField('Находится ли в корзине')
    pub_date = models.DateTimeField('Дата публикации', auto_now_add=True)
    author = models.ForeignKey(
        ApiUser,
        on_delete=models.CASCADE,
#        related_name='recipe_author',
        null=True, blank=True
    )

    tags = models.ManyToManyField(
        'Tag',
        through='TagsInRecipe',
#        related_name='recipes',
        verbose_name='Тэги'
    )

    ingredients = models.ManyToManyField(
        'Ingredient',
        through='IngredientInRecipe',
#        related_name='ingredients'
        verbose_name='Ингредиенты'
    )



    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ['pub_date']

    def __str__(self):
        return self.name



class IngredientInRecipe(models.Model):

    ingredient = models.ForeignKey(
        Ingredient,
        related_name='ingredient_in_recipe',
        on_delete=models.CASCADE,
        verbose_name='Ингредиент'
    )
    recipe = models.ForeignKey(
        Recipe,
        related_name='ingredient_in_recipe',
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
        ApiUser,
        related_name='recipe_in_cart',
        on_delete=models.CASCADE,
        verbose_name='Пользователь'
    )

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'


class Subscription(models.Model):
    pass
    #
    # subscriber = models.ForeignKey(
    #     ApiUser,
    #     verbose_name='Подписчик',
    #     related_name='subscriber',
    #     on_delete=models.CASCADE,
    # )
    #
    # author = models.ForeignKey(
    #     ApiUser,
    #     verbose_name="Автор рецепта",
    #     related_name="author",
    #     on_delete=models.CASCADE,
    # )
    # class Meta:
    #     verbose_name = 'Подписка на пользователя'
    #     verbose_name_plural = 'Подписки на пользователей'
    #     ordering = ('subscriber', 'author')
    #     constraints = [models.UniqueConstraint(
    #         fields=['subscriber', 'author'],
    #         name='subscription_unique'
    #         )
    #     ]
    #
    # def __str__(self):
    #     return f"{self.subscriber} подписан на {self.author}"
    #
    # def clean(self):
    #     if self.subscriber == self.author:
    #         raise BadRequest('На себя не подписаться')




class Favorite(models.Model):
    user = models.ForeignKey(
        ApiUser,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Рецепт',
    )

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'
        constraints = [models.UniqueConstraint(
            fields=['user', 'recipe'],
            name='unique_favourite')
        ]

    def __str__(self):
        return f'{self.user} добавил "{self.recipe}" в Избранное'

class TagsInRecipe(models.Model):

    recipe = models.ForeignKey('Recipe', on_delete=models.CASCADE)
    tag = models.ForeignKey('Tag', on_delete=models.CASCADE)



class UserAdmin(admin.ModelAdmin):
    pass
    # list_display = ('username', 'email', 'role')
    # search_fields = ('username', 'email', 'role')
    # list_filter = ('role',)