from rest_framework import serializers, generics
from djoser.serializers import UserCreateSerializer, UserSerializer
from .models import Recipe, Ingredient, Tag, IngredientInRecipe, ApiUser, ShopingCart, Favorite, Subscription  # , User
from .validators import username_validator
from backend.constants import MAX_NAME_LENGTH
from rest_framework.fields import IntegerField, SerializerMethodField
from drf_extra_fields.fields import Base64ImageField

class ApiUserCreateSerializer(UserCreateSerializer):
    """Сериализатор для модели User"""

    class Meta(UserCreateSerializer.Meta):
        model = ApiUser
        fields = (
            "username",
            "first_name",
            "last_name",
            "email",
            "password"
        )
class ApiUserSerializer(UserSerializer):
    """Сериализатор для модели ApiUser"""

    username = serializers.CharField(
        max_length=MAX_NAME_LENGTH,
#        validators=[username_validator]
    )
    # is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = ApiUser
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'avatar'
        )


class ApiUserListSerializer(UserSerializer):
    class Meta:
        model = ApiUser
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            #            'avatar'
        )


class UserMeRoleSerializer(ApiUserSerializer):
    role = serializers.CharField()


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug')

class IngredientSerializer(serializers.ModelSerializer):

    # name = serializers.CharField(required=True)
    # measurment_unit = serializers.CharField(required=True)
    #     # 'Единицы измерения',
    #     # max_length=128,
    # # )

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class IngredientInRecipeSerializer(serializers.ModelSerializer):
#    name = IngredientSerializer(source='*')

    class Meta:
        model = IngredientInRecipe
        fields = ('name', 'recipe', 'amount')


class ShopingCartSerializer(serializers.ModelSerializer):

    class Meta:
        model = ShopingCart
        fields = (

        )


class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorite
        fields = (

        )


class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = (

        )


class RecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    author = ApiUserSerializer(read_only=True)
    ingredients = SerializerMethodField()
    is_favorited = SerializerMethodField(read_only=True)
    is_in_shopping_cart = SerializerMethodField(read_only=True)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients', 'is_favorited',
                  'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time')



