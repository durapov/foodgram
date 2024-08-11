from rest_framework import serializers, generics
from djoser.serializers import UserCreateSerializer, UserSerializer
from .models import Recipe, Ingredient, Tag, IngredientInRecipe, ApiUser, ShopingCart, Favorite, Subscription  # , User
from .validators import username_validator
from backend.constants import MAX_NAME_LENGTH



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
        fields = ('id', 'name', 'color', 'slug')

class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ('name', 'measurment_unit')


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
    tags = TagSerializer(many=True)
    ingredients = IngredientInRecipeSerializer(many=True)

    class Meta:
        model = Recipe
        fields = ('tags', 'author', 'ingredients', 'is_favorited', 'is_in_shopping_cart',
                  'name', 'image', 'text')



