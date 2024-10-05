from django.core.files.base import ContentFile
from django.db import transaction
from django.shortcuts import get_object_or_404
from djoser.serializers import UserCreateSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from .models import (Favorite, Ingredient, IngredientInRecipe, Recipe,
                     ShoppingList, Subscribe, Tag, User)
from backend.constants import (MAX_COOKING_TIME, MAX_INGREDIENTS,
                               MIN_COOKING_TIME, MIN_INGREDIENTS)


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


class TagSerializer(ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug')


class IngredientSerializer(ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')
        read_only_fields = ('__all__',)


class IngredientInRecipeSerializer(serializers.ModelSerializer):
    amount = serializers.IntegerField(
        min_value=MIN_INGREDIENTS,
        max_value=MAX_INGREDIENTS,
        default=None
    )

    class Meta:
        model = IngredientInRecipe
        fields = ('recipe', 'ingredient', 'amount')

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        new_representation = {
            'id': instance.id,
            'name': instance.ingredient.name,
            'measurement_unit': instance.ingredient.measurement_unit,
            'amount': representation['amount']
        }
        return new_representation


class RecipeGetSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    tags = TagSerializer(read_only=True, many=True)
    ingredients = IngredientInRecipeSerializer(many=True).data
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    def to_representation(self, instance):
        data = super().to_representation(instance)
        ingredients = instance.recipes_ingredients.all()
        data['ingredients'] = IngredientInRecipeSerializer(
            ingredients,
            many=True
        ).data
        return data

    def get_is_favorited(self, obj):
        request = self.context['request']
        if request.user.is_authenticated:
            return request.user.favorite_users.filter(
                recipes=obj).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        request = self.context['request']
        if request.user.is_authenticated:
            return request.user.shoppinglist_users.filter(
                recipes=obj).exists()
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
        required=True,
        min_value=MIN_COOKING_TIME,
        max_value=MAX_COOKING_TIME
    )

    def validate(self, data):
        data = super().validate(data)
        request = self.context['request']
        get_tags = request.data.get('tags')
        tags_data = set()
        if not get_tags:
            raise serializers.ValidationError(
                {'tags': ['Обязательное поле.']})
        for tag_data in get_tags:
            try:
                tag = Tag.objects.get(pk=tag_data)
                if tag in tags_data:
                    raise serializers.ValidationError(
                        {'tags': ['Такой тэг уже есть.']})
                tags_data.add(tag)
            except Tag.DoesNotExist:
                raise serializers.ValidationError(
                    {'Tag': ['Такого тэга нет.']})
        get_ingredients = request.data.get('ingredients')
        if not get_ingredients:
            raise serializers.ValidationError(
                {'ingredients': ['Обязательное поле.']})
        ingredients_set = set()
        ingredients_data = []
        for ingredient in get_ingredients:
            if ingredient['amount'] <= 0:
                raise serializers.ValidationError(
                    {'amount': ['Количество не меньше 1']})
            if ingredient['id'] in ingredients_set:
                raise serializers.ValidationError(
                    {'ingredients': ['Такой id занят.']})
            ingredients_set.add(ingredient['id'])
            try:
                ingredients = Ingredient.objects.filter(id__in=ingredients_set)
                ingredients_data.append(
                    {'ingredient': ingredients.get(pk=ingredient['id']),
                     'amount': ingredient['amount']})
            except Ingredient.DoesNotExist:
                raise serializers.ValidationError(
                    {'ingredients': ['Такого ингредиента нет.']})
        data['ingredients'] = ingredients_data
        data['tags'] = tags_data
        return data

    def validate_image(self, value):
        if not value:
            raise serializers.ValidationError({'image': 'Обязательное поле.'})
        return value

    def create_ingredients(self, data, recipe):

        IngredientInRecipe.objects.bulk_create(
            [IngredientInRecipe(recipe=recipe, **ingredient_data)
             for ingredient_data in data],
        )

    @transaction.atomic
    def update(self, instance, validated_data):
        instance.ingredients.clear()
        instance.tags.set(validated_data.pop('tags'))
        self.create_ingredients(validated_data.pop('ingredients'),
                                recipe=instance)
        validated_data['is_favorited'] = self.get_is_favorited(instance)
        return super().update(instance, validated_data)

    @transaction.atomic
    def create(self, validated_data):
        validated_data.pop('is_favorited', None)
        validated_data.pop('is_in_shopping_cart', None)
        tags_data = validated_data.pop('tags')
        ingredients_data = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        for ingredient_data in ingredients_data:
            ingredient = ingredient_data['ingredient']
            amount = ingredient_data['amount']
            IngredientInRecipe.objects.create(recipe=recipe,
                                              ingredient=ingredient,
                                              amount=amount)
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
        user_id = self.context['view'].kwargs.get('id')
        user = get_object_or_404(User, pk=user_id)
        if request.user == user:
            raise serializers.ValidationError(
                {'subscriber': ['На себя не подписаться.']})
        if (request.method == 'POST' and request.user.subscription_author
                .filter(subscriber=user).exists()):
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
        request = self.context['request']
        recipe_id = self.context['view'].kwargs.get('pk')
        recipe = get_object_or_404(Recipe, pk=recipe_id)
        if request.method == 'POST' and request.user.shoppinglist_users.filter(
                recipes=recipe).exists():
            raise serializers.ValidationError(
                {'recipes': ['Рецепт уже в корзине.']})
        return data

    class Meta:
        model = ShoppingList
        fields = ('recipes',)
        read_only_fields = ('user', 'recipes')


class FavoriteSerializer(ShoppingListSerializer):
    def validate(self, data):
        request = self.context['request']
        recipe_id = self.context['view'].kwargs.get('pk')
        if not Recipe.objects.filter(pk=recipe_id).exists():
            raise serializers.ValidationError(
                {'recipes': ['Такого рецепта нет.']})
        if request.method == 'POST' and request.user.favorite_users.filter(
                recipes__id=recipe_id).exists():
            raise serializers.ValidationError(
                {'recipes': ['Рецепт уже в избранном.']})

        return data

    class Meta:
        model = Favorite
        fields = ('recipes',)
        read_only_fields = ('user', 'recipes')
