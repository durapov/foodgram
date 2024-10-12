import csv
import io

from django.db.models import Exists, OuterRef, Sum
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.serializers import SetPasswordSerializer
from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework import filters, status
from rest_framework.decorators import action
from rest_framework.pagination import (LimitOffsetPagination,
                                       PageNumberPagination)
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from .filters import IngredientFilter, RecipeFilter
from .models import (Favorite, Ingredient, IngredientInRecipe, Recipe,
                     ShoppingList, Subscribe, Tag, User)
from .permissions import CustomPermission
from .serializers import (AvatarSerializer, CustomUserCreateSerializer,
                          FavoriteSerializer, IngredientSerializer,
                          RecipeGetSerializer, RecipeWriteSerializer,
                          ShoppingListSerializer, SubscribeSerializer,
                          TagSerializer, UserSerializer,
                          IngredientInRecipeSerializer)
from backend.constants import PAGE_SIZE


class PaginationNone(PageNumberPagination):
    page_size = None


class CustomPagination(PageNumberPagination):
    page_size = PAGE_SIZE
    page_size_query_param = 'limit'


class IngredientViewSet(ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = PaginationNone
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter


class IngredientInRecipeViewSet(ReadOnlyModelViewSet):
    queryset = IngredientInRecipe.objects.all()
    serializer_class = IngredientInRecipeSerializer
    pagination_class = PaginationNone
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter


class TagViewSet(ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = PaginationNone


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.prefetch_related('author', 'ingredients',
                                               'tags')
    permission_classes = [IsAuthenticatedOrReadOnly, CustomPermission]
    pagination_class = CustomPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    http_method_names = ['get', 'post', 'patch', 'delete']
    serializer_class = RecipeWriteSerializer
    pk_url_kwarg = 'pk'

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            favorites = user.favorite_users.filter(
                recipes=OuterRef('pk'))
            shopping_cart = user.shoppinglist_users.filter(
                recipes=OuterRef('pk'))
            subscribers = user.subscription_author.filter(
                subscriber=OuterRef('author'))
            return super().get_queryset().annotate(
                is_favorite=Exists(favorites),
                is_in_shopping_cart=Exists(shopping_cart),
                is_subscribed=Exists(subscribers)
            )
        return super().get_queryset()

    def get_serializer_class(self):
        if self.action in ['shopping_cart', 'download_shopping_cart']:
            return ShoppingListSerializer
        if self.action == 'favorite':
            return FavoriteSerializer
        if self.request.method == 'GET':
            return RecipeGetSerializer
        if self.request.method == 'PATCH':
            return RecipeWriteSerializer
        return super().get_serializer_class()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def recipe_post(self):
        request_user = self.request.user
        get_recipe = get_object_or_404(Recipe,
                                       pk=self.kwargs[self.pk_url_kwarg])
        serializer = self.get_serializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request_user, recipes=get_recipe)
        get_headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED,
                        headers=get_headers)

    def recipe_delete(self, manager):
        request_user = self.request.user
        get_recipe = get_object_or_404(Recipe,
                                       pk=self.kwargs[self.pk_url_kwarg])
        recipe = manager.filter(user=request_user, recipes=get_recipe)
        if recipe.exists():
            recipe.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['post'], detail=True, )
    def shopping_cart(self, request, pk=None):
        return self.recipe_post()

    @shopping_cart.mapping.delete
    def delete_shopping_cart(self, request, pk=None):
        return self.recipe_delete(ShoppingList.objects)

    @action(methods=['get'], detail=False, )
    def download_shopping_cart(self, request, pk=None):
        shop_list = get_shop_list(self.request.user)
        response = FileResponse(iter([shop_list.getvalue()]),
                                content_type='text/csv')
        response[
            'Content-Disposition'] = 'attachment; filename="shopping_cart.csv"'
        return response

    @action(methods=['post'], detail=True, )
    def favorite(self, request, pk=None):
        return self.recipe_post()

    @favorite.mapping.delete
    def delete_favorite(self, request, pk=None):
        return self.recipe_delete(Favorite.objects)

    @action(methods=['GET'], detail=True, url_path='get-link')
    def get_link(self, request, pk):
        get_object_or_404(Recipe, id=pk)
        url = request.build_absolute_uri(f'/recipes/{pk}/')
        return Response({'short-link': url}, status=status.HTTP_200_OK)


class UserViewSet(DjoserUserViewSet):
    pagination_class = LimitOffsetPagination
    filter_backends = [filters.SearchFilter]
    pk_url_kwarg = 'id'
    search_fields = ['username']
    http_method_names = ['get', 'post', 'put', 'delete']

    def get_queryset(self):
        user = self.request.user
        queryset = User.objects.all()
        if user.is_authenticated:
            subscribers_all = user.subscribers.all()
            subscribers = subscribers_all.values_list('user', flat=True)
            queryset = queryset.annotate(
                is_subscribed=Exists(Subscribe.objects.filter(
                    user__in=subscribers,
                    subscriber=OuterRef('pk')
                ))
            )
        return queryset

    def get_permissions(self):
        if self.action == 'me':
            self.permission_classes = [IsAuthenticated]
        return super().get_permissions()

    @action(detail=True, methods=['post'],
            permission_classes=[IsAuthenticated])
    def subscribe(self, request, *args, **kwargs):
        request_user = self.request.user
        get_user = get_object_or_404(User, pk=kwargs[self.pk_url_kwarg])
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request_user, subscriber=get_user)
        get_headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED,
                        headers=get_headers)

    @action(detail=False, methods=['get'],
            permission_classes=[IsAuthenticated])
    def subscriptions(self, request, *args, **kwargs):
        request_users = self.request.user.subscription_author.all()
        paginate = self.paginate_queryset(request_users)
        serializer = self.get_serializer(paginate, many=True)
        serializer = self.get_paginated_response(serializer.data)
        return Response(serializer.data)

    @action(detail=False, methods=['put'],
            permission_classes=[IsAuthenticated],
            url_path='me/avatar', )
    def avatar(self, request, *args, **kwargs):
        request_user = self.request.user
        serializer = AvatarSerializer(instance=request_user, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'avatar': request_user.avatar.url})

    @avatar.mapping.delete
    def delete_avatar(self, request, *args, **kwargs):
        user = self.request.user
        user.avatar.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @subscribe.mapping.delete
    def unsubscribe(self, request, *args, **kwargs):
        request_user = self.request.user
        get_user = get_object_or_404(User, pk=kwargs[self.pk_url_kwarg])
        subscription = request_user.subscription_author.filter(
            subscriber=get_user).first()
        if subscription:
            subscription.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    def get_serializer_class(self):
        if self.action in ['subscriptions', 'subscribe']:
            return SubscribeSerializer
        if self.action == 'set_password':
            return SetPasswordSerializer
        if self.action == 'create':
            return CustomUserCreateSerializer
        return UserSerializer


def get_shop_list(user):
    """Получить список покупок"""
    count_ingredients = {}
    shop_list = io.StringIO()
    writer = csv.writer(shop_list)
    writer.writerow(['Ингредиент', 'Количество'])
    user_shopping_list = user.shoppinglist_users.all()
    ingredients = (IngredientInRecipe.objects.filter(
        recipe__in=user_shopping_list.values_list('recipes',
                                                  flat=True)).values(
        'ingredient__name').annotate(total_amount=Sum('amount')))
    for item in ingredients:
        count_ingredients[item['ingredient__name']] = item['total_amount']
    for key, value in count_ingredients.items():
        writer.writerow([key, value])
    shop_list.seek(0)
    return shop_list
