from django.core.files.base import ContentFile
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import transaction
from djoser.serializers import UserCreateSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from backend.constants import (MAX_COOKING_TIME, MIN_COOKING_TIME)

from .models import (Favorite, Ingredient, IngredientInRecipe, Recipe,
                     ShoppingList, Subscribe, Tag, User)


class CustomUserCreateSerializer(UserCreateSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'first_name',
                  'last_name', 'password')
        required_fields = ('username', 'first_name', 'last_name')


class UserSerializer(UserCreateSerializer):
    is_subscribed = serializers.SerializerMethodField()

    def get_is_subscribed(self, obj):
        return getattr(obj, 'is_subscribed', False)

    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'first_name',
                  'last_name', 'avatar', 'password', 'is_subscribed')
        required_fields = ('username', 'first_name', 'last_name')


class IngredientSerializer(ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')
        extra_kwargs = {'measurement_unit': {'read_only': True}}
        read_only_fields = ('id',)


class TagSerializer(ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug')


class IngredientInRecipeSerializer(serializers.ModelSerializer):
    ingredient = IngredientSerializer(
        read_only=True,
    )

    class Meta:
        model = IngredientInRecipe
        fields = ('ingredient', 'amount')

    def to_representation(self, instance):
        data = super().to_representation(instance)
        ingredient = data['ingredient']
        ingredient['amount'] = data['amount']
        return ingredient


class RecipeGetSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    ingredients = serializers.SerializerMethodField()
    tags = TagSerializer(read_only=True, many=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    def get_ingredients(self, obj):
        return IngredientInRecipeSerializer(
            obj.recipes_ingredients.all(), many=True,
        ).data

    def get_is_favorited(self, obj):
        request = Favorite.objects.all()
        fav_recipes = []
        for i in request:
            fav_recipe = i.recipes
            fav_recipes.append(fav_recipe)
        if obj in fav_recipes:
            return True
        else:
            return False

    def get_is_in_shopping_cart(self, obj):
        request = ShoppingList.objects.all()
        shopping_cart_recipes = []
        for i in request:
            shopping_card_item = i.recipes
            shopping_cart_recipes.append(shopping_card_item)
        if obj in shopping_cart_recipes:
            return True
        else:
            return False

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients', 'is_favorited',
                  'is_in_shopping_cart', 'name', 'image', 'text',
                  'cooking_time')


class RecipeWriteSerializer(RecipeGetSerializer):
    image = Base64ImageField(required=True)
    is_favorited = serializers.BooleanField(default=False)
    is_in_shopping_cart = serializers.BooleanField(default=False)
    cooking_time = serializers.IntegerField(
        required=True, validators=[
            MinValueValidator(MIN_COOKING_TIME, message='Не менее 1 минуты.'),
            MaxValueValidator(MAX_COOKING_TIME,
                              message='Не более 32000 минут.')
        ]
    )

    def validate(self, data):
        data = super().validate(data)
        request = self.context['request']
        get_tags = request.data.get('tags')
        get_ingredients = request.data.get('ingredients')
        if not get_ingredients:
            raise serializers.ValidationError(
                {'ingredients': ['Обязательное поле.']})
        ingredients_set = set()
        ingredients_data = []
        for ingredient in get_ingredients:
            if ingredient['id'] in ingredients_set:
                raise serializers.ValidationError(
                    {'ingredients': ['Такой id занят.']})
            try:
                if int(ingredient.get('amount')) < 1:
                    raise serializers.ValidationError(
                        {'amount': ['Должно быть не меньше 1.']})
            except ValueError:
                raise serializers.ValidationError(
                    {'amount': ['Должно быть целое число.']})
            ingredients_set.add(ingredient['id'])
        try:
            ingredients = Ingredient.objects.filter(id__in=ingredients_set)
            for ingredient in get_ingredients:
                ingredients_data.append(
                    {'ingredient': ingredients.get(pk=ingredient['id']),
                     'amount': ingredient['amount']})
        except Ingredient.DoesNotExist:
            raise serializers.ValidationError(
                {'ingredients': ['Такого ингредиента нет.']})
        tags_data = []
        if not get_tags:
            raise serializers.ValidationError(
                {'tags': ['Обязательное поле.']})
        for tag_data in get_tags:
            try:
                tag = Tag.objects.get(pk=tag_data)
                if tag in tags_data:
                    raise serializers.ValidationError(
                        {'tags': ['Такой тэг уже есть.']})
                else:
                    tags_data.append(tag)
            except Tag.DoesNotExist:
                raise serializers.ValidationError(
                    {'Tag': ['Такого тэга нет.']})
        data['ingredients'] = ingredients_data
        data['tags'] = tags_data
        return data

    def validate_image(self, value):
        if not value:
            raise serializers.ValidationError({'image': 'Обязательное поле.'})
        return value

    def create_ingredients(self, data, recipe):
        ingredients_data = [{'ingredient': ingredient_data['ingredient'],
                             'amount': ingredient_data['amount']}
                            for ingredient_data in data
                            ]
        IngredientInRecipe.objects.bulk_create(
            [IngredientInRecipe(recipe=recipe, **ingredient_data)
             for ingredient_data in ingredients_data],
        )

    @transaction.atomic
    def update(self, instance, validated_data):
        instance.ingredients.clear()
        instance.tags.set(validated_data.pop('tags'))
        self.create_ingredients(validated_data.pop('ingredients'), instance)
        validated_data['is_favorited'] = self.get_is_favorited(instance)
        return super().update(instance, validated_data)

    @transaction.atomic
    def create(self, validated_data):
        tags_data = validated_data.pop('tags')
        ingredients_data = validated_data.pop('ingredients')
        validated_data.pop('is_favorited')
        validated_data.pop('is_in_shopping_cart')
        recipe = Recipe.objects.create(**validated_data)
        self.create_ingredients(ingredients_data, recipe)
        recipe.tags.set(tags_data)
        return recipe


class UserWithRecipeSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    email = serializers.EmailField()
    username = serializers.CharField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    avatar = Base64ImageField()
    is_subscribed = serializers.BooleanField(default=False)
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj).count()

    def get_recipes(self, obj):
        recipes_limit = self.context['request'].query_params.get(
            'recipes_limit', None)
        if recipes_limit:
            recipes = obj.recipe.all()
            recipes = recipes[:int(recipes_limit)]
        else:
            recipes = obj.recipe.all()
        return ShortRecipeSerializer(recipes, many=True).data

    class Meta:
        fields = ('id', 'email', 'username', 'first_name', 'last_name',
                  'avatar', 'is_subscribed', 'recipes', 'recipes_count')


class SubscribeSerializer(serializers.ModelSerializer):
    subscriber = UserSerializer(read_only=True)

    def to_representation(self, instance):
        return UserWithRecipeSerializer(
            instance.subscriber, context=self.context).data

    def validate(self, data):
        request = self.context['request']
        try:
            user = User.objects.get(pk=self.context['view'].kwargs.get('id'))
        except User.DoesNotExist:
            raise serializers.ValidationError(
                {'subscriber': ['Такого пользователя нет.']})
        if request.user == user:
            raise serializers.ValidationError(
                {'subscriber': ['На себя не подписаться.']})
        if (request.method == 'POST' and Subscribe.objects.filter(
                user=request.user, subscriber=user).exists()):
            raise serializers.ValidationError(
                {'non_field_errors': [
                    'Вы подписались на пользователя ранее.']})
        return data

    class Meta:
        model = Subscribe
        fields = ('subscriber',)
        read_only_fields = ('user', 'subscriber')


class ShortRecipeSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    image = Base64ImageField()
    cooking_time = serializers.IntegerField()

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class AvatarSerializer(serializers.ModelSerializer):
    avatar = Base64ImageField(required=True)

    def update(self, instance, validated_data):
        avatar_data = validated_data.get('avatar', None)
        file_avatar = ContentFile(avatar_data.read())
        instance.avatar.save('image.png', file_avatar, save=True)
        return instance

    def validate_avatar(self, avatar_data):
        if not avatar_data:
            raise serializers.ValidationError('Пустой запрос.')
        return avatar_data

    class Meta:
        model = User
        fields = ('avatar',)


class ShoppingListSerializer(serializers.ModelSerializer):
    recipes = RecipeGetSerializer(read_only=True)

    def to_representation(self, instance):
        return ShortRecipeSerializer(
            instance.recipes, context=self.context).data

    def validate(self, data):
        request_context = self.context['request']
        try:
            recipes_get = Recipe.objects.get(
                pk=self.context['view'].kwargs.get('pk'))
        except Recipe.DoesNotExist:
            raise serializers.ValidationError(
                {'recipes': ['Такого рецепта нет.']})
        if (request_context.method == 'POST'
                and ShoppingList.objects.filter(
                    user=request_context.user, recipes=recipes_get).exists()):
            raise serializers.ValidationError(
                {'recipes': ['Рецепт уже в корзине.']})
        return data

    class Meta:
        model = ShoppingList
        fields = ('recipes',)
        read_only_fields = ('user', 'recipes')


class FavoriteSerializer(ShoppingListSerializer):

    def validate(self, data):
        request_context = self.context['request']
        try:
            recipes_get = Recipe.objects.get(
                pk=self.context['view'].kwargs.get('pk'))
        except Recipe.DoesNotExist:
            raise serializers.ValidationError(
                {'recipes': ['Такого рецепта нет.']})
        if (request_context.method == 'POST' and Favorite.objects.filter(
                user=request_context.user, recipes=recipes_get).exists()):
            raise serializers.ValidationError(
                {'recipes': ['Рецепт уже в избранном.']})
        return data

    class Meta:
        model = Favorite
        fields = ('recipes',)
        read_only_fields = ('user', 'recipes')
