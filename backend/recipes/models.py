from django.contrib.auth import hashers
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import CheckConstraint, UniqueConstraint
from django.utils.translation import gettext_lazy
from rest_framework.exceptions import ValidationError

from backend.constants import (EMAIL_LENGTH, INGREDIENT_LENGTH,
                               MAX_COOKING_TIME, MAX_INGREDIENTS,
                               MEASURMENT_LENGTH,
                               MIN_COOKING_TIME, MIN_INGREDIENTS, NAME_LENGTH,
                               RECIPE_LENGTH, ROLE_LENGTH, SLUG_LENGTH,
                               TAG_LENGTH)


def user_validator(value):
    if value == 'me':
        raise ValidationError('Неверный логин')


class User(AbstractUser):
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = [
        'first_name',
        'last_name',
    ]

    class Roles(models.TextChoices):
        ADMIN = 'admin', gettext_lazy('Admin')
        USER = 'user', gettext_lazy('User')

    username = models.CharField(
        'Логин',
        max_length=NAME_LENGTH,
        unique=True,
        validators=[
            UnicodeUsernameValidator(),
            user_validator
        ],
    )
    first_name = models.CharField(
        'Имя',
        max_length=NAME_LENGTH
    )
    last_name = models.CharField(
        'Фамилия',
        max_length=NAME_LENGTH
    )
    email = models.EmailField(
        verbose_name='email',
        max_length=EMAIL_LENGTH,
        unique=True,
    )
    avatar = models.ImageField(
        verbose_name='Аватар',
        upload_to='users/',
        null=True,
        blank=True
    )
    role = models.CharField(
        'Роль',
        max_length=ROLE_LENGTH,
        default=Roles.USER,
        choices=Roles.choices,
    )

    class Meta:
        ordering = ['username', 'email']
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def set_password(self, set_pass):
        self.password = hashers.make_password(set_pass)

    def update_password(self, old_pass, new_pass):
        if not self.check_password(old_pass):
            raise ValueError('Неверный пароль.')
        self.set_password(new_pass)
        self.save()

    def check_password(self, check_pass):
        return hashers.check_password(check_pass, self.password)

    @property
    def is_admin(self):
        return self.role == self.Roles.ADMIN or self.is_superuser

    def __str__(self):
        return self.username


class Subscribe(models.Model):
    user = models.ForeignKey(
        User,
        related_name='subscription_author',
        verbose_name='Автор',
        on_delete=models.CASCADE,
    )
    subscriber = models.ForeignKey(
        User,
        related_name='subscribers',
        verbose_name='Подписчик',
        on_delete=models.CASCADE,
    )

    class Meta:
        ordering = ('user',)
        constraints = [
            UniqueConstraint(fields=['user', 'subscriber'],
                             name='unique_subscribers'),
            CheckConstraint(
                name='self_subscribing_constraint',
                check=~models.Q(user=models.F('subscriber')),
            ),
        ]
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'

    def __str__(self):
        return f'{self.subscriber} подписан на {self.user}'

    def clean(self):
        if self.user == self.subscriber:
            raise ValidationError('Нельзя подписаться на себя')


class Ingredient(models.Model):
    name = models.CharField(
        verbose_name='Название',
        max_length=INGREDIENT_LENGTH,
        unique=True
    )
    measurement_unit = models.CharField(
        verbose_name='Единица измерения ингредиента',
        max_length=MEASURMENT_LENGTH
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(
        verbose_name='Тэг (название)',
        unique=True,
        max_length=TAG_LENGTH
    )
    slug = models.SlugField(
        verbose_name='Слаг',
        unique=True,
        max_length=SLUG_LENGTH
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        related_name='recipe',
        on_delete=models.CASCADE,
        verbose_name='Автор рецепта',
    )
    name = models.CharField(
        verbose_name='Название рецепта',
        max_length=RECIPE_LENGTH,
        unique=True
    )
    text = models.TextField(
        verbose_name='Описание рецепта'
    )
    image = models.ImageField(
        verbose_name='Изображение рецепта',
        upload_to='recipes/',
        null=True,
        blank=True
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления',
        validators=[MinValueValidator(MIN_COOKING_TIME,
                                      message='Не менее 1 минуты.'),
                    MaxValueValidator(MAX_COOKING_TIME,
                                      message='Не более 32000 минут.')
                    ],
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientInRecipe',
        related_name='recipes',
        verbose_name='Ингредиенты',

    )

    tags = models.ManyToManyField(
        Tag,
        related_name='tag_recipes',
        verbose_name='Тэги'
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class IngredientInRecipe(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipes_ingredients',
        verbose_name='Рецепт'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        related_name='ingredients_in_recipes',
        on_delete=models.CASCADE,
        verbose_name='Ингредиент'
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество',
        validators=[
            MinValueValidator(MIN_INGREDIENTS,
                              message='Добавьте хотя бы 1 ингредиент.'),
            MaxValueValidator(MAX_INGREDIENTS,
                              message='Не более 32000 ингредиентов.')
        ],
    )

    class Meta:
        ordering = ('recipe',)
        verbose_name = 'Ингредиент в рецепте'
        verbose_name_plural = 'Ингредиенты в рецептах'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='unique_IngredientInRecipe'), ]


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorite_users',
        verbose_name='Пользователь',
    )
    recipes = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorite_recipes',
        verbose_name='Рецепт',
    )

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'
        ordering = ['user']


class ShoppingList(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shoppinglist_users',
        verbose_name='Пользователь',
    )
    recipes = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shoppinglist_recipes',
        verbose_name='Рецепт',
    )

    class Meta:
        ordering = ['user']
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзины'
        constraints = [
            UniqueConstraint(fields=['user', 'recipes'],
                             name='unique_shopping_cart')
        ]

    def __str__(self):
        return f'{self.user} добавил рецепт "{self.recipes}" в Корзину'
