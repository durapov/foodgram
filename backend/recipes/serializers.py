from rest_framework import serializers, generics
from djoser.serializers import UserCreateSerializer, UserSerializer
from .models import Recipe, Ingredient, Tag, IngredientInRecipe, ApiUser, ShopingCart, Favorite, Subscription  # , User
from .validators import username_validator
from backend.constants import MAX_NAME_LENGTH
from rest_framework.fields import IntegerField, SerializerMethodField
from drf_extra_fields.fields import Base64ImageField
from django.db.models import F


class ApiUserSerializer(UserSerializer):
    """Сериализатор для модели ApiUser"""

    username = serializers.CharField(
        max_length=MAX_NAME_LENGTH,
#        validators=[username_validator]
    )
    #is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = ApiUser
        fields = [
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'avatar'
        ]

    # def get_is_subscribed(self, obj):
    #     user = self.context.get('request').user
    #     if user.is_anonymous:
    #         return False
    #     return Subscription.objects.filter(user=user, author=obj).exists()


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ['id', 'name', 'slug']


class IngredientSerializer(serializers.ModelSerializer):

    # name = serializers.CharField(required=True)
    # measurment_unit = serializers.CharField(required=True)
    #     # 'Единицы измерения',
    #     # max_length=128,
    # # )

    class Meta:
        model = Ingredient
        fields = ['id', 'name', 'measurement_unit']


class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorite
        fields = ['user', 'recipe']


class RecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    author = ApiUserSerializer(many=True, read_only=True)
    ingredients = SerializerMethodField()
    is_favorited = SerializerMethodField(read_only=True)
    is_in_shopping_cart = SerializerMethodField(read_only=True)
    image = Base64ImageField()

    def get_ingredients(self, obj):
        return list(
            obj.ingredient_in_recipe.select_related('ingredient').values(
                'ingredient__id', 'ingredient__name', 'ingredient__measurement_unit', 'amount',
            )
        )

    def get_is_favorited(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return user.favorites.filter(recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return not user.recipe_in_cart.filter(recipe=obj).exists()

    # def create(self, validated_data):
    #     author = self.context.get('request').user
    #     tags = validated_data.pop('tags')
    #     ingredients = validated_data.pop('ingredients')
    #     recipe = Recipe.objects.create(author=author, **validated_data)
    #     self.create_tags(tags, recipe)
    #     self.create_ingredients(ingredients, recipe)
    #     return recipe



    class Meta:
        model = Recipe
        fields = ['id', 'tags', 'author', 'ingredients', 'is_favorited',
                  'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time']







# class ApiUserCreateSerializer(UserCreateSerializer):
#     """Сериализатор для модели User"""
#
#     class Meta(UserCreateSerializer.Meta):
#         model = ApiUser
#         fields = (
#             "username",
#             "first_name",
#             "last_name",
#             "email",
#             "password"
#         )
#
# class ApiUserListSerializer(UserSerializer):
#     class Meta:
#         model = ApiUser
#         fields = (
#             'email',
#             'id',
#             'username',
#             'first_name',
#             'last_name',
#             'is_subscribed',
#             #            'avatar'
#         )
#
#
# class UserMeRoleSerializer(ApiUserSerializer):
#     role = serializers.CharField()


#
# class IngredientInRecipeSerializer(serializers.ModelSerializer):
# #    name = IngredientSerializer(source='*')
#
#     class Meta:
#         model = IngredientInRecipe
#         fields = ('name', 'recipe', 'amount')
#
#
# class ShopingCartSerializer(serializers.ModelSerializer):
#
#     class Meta:
#         model = ShopingCart
#         fields = (
#
#         )
#
#


#
#
# class SubscriptionSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Subscription
#         fields = (
#
#         )



