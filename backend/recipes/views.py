import csv
import io

from django.db.models import Exists, OuterRef, Sum
from django.http import FileResponse
from django.shortcuts import get_object_or_404, redirect
from django_filters.rest_framework import DjangoFilterBackend
from djoser.serializers import SetPasswordSerializer
from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework import filters, status
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination, \
    PageNumberPagination
from rest_framework.permissions import IsAuthenticated, \
    IsAuthenticatedOrReadOnly
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
                          TagSerializer, UserSerializer)


class PaginationNone(PageNumberPagination):
    page_size = None


class CustomPagination(PageNumberPagination):
    page_size = 6
    page_size_query_param = 'limit'


class IngredientViewSet(ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = PaginationNone
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter


class TagViewSet(ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = PaginationNone


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.prefetch_related('author', 'ingredients', 'tags')
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
            favorites = Favorite.objects.filter(
                recipes=OuterRef('pk'), user=user)
            shopping_cart = ShoppingList.objects.filter(
                recipes=OuterRef('pk'), user=user)
            subscribers = Subscribe.objects.filter(
                subscriber=OuterRef('author'), user=user)
            return super().get_queryset().annotate(
                is_favorite=Exists(favorites),
                is_in_shopping_cart=Exists(shopping_cart),
                is_subscribed=Exists(subscribers)
            )
        return super().get_queryset()

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
        if manager.filter(user=request_user, recipes=get_recipe).exists():
            manager.filter(user=request_user, recipes=get_recipe).delete()
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

    @action(methods=['get'], detail=True, url_path='get-link')
    def get_link(self, request, pk=None):
        get_recipe = self.get_object()
        base_url = request.get_host()
        short_link = f'https://{base_url}/s/{get_recipe.short_link}'
        return Response({'short-link': short_link})

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
            subscribers = Subscribe.objects.filter(
                subscriber=OuterRef('pk'), user=user)
            queryset = queryset.annotate(
                is_subscribed=Exists(subscribers))
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
        unsubscribe, _ = Subscribe.objects.filter(
            user=request_user, subscriber=get_user).delete()
        if unsubscribe:
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


def get_recipe_short_link(request, short_link):
    """Получить короткую ссылку на рецепт"""
    base_url = request.get_host()
    get_recipe = get_object_or_404(Recipe.objects, short_link=short_link)
    return redirect(f'http://{base_url}/recipes/{get_recipe.pk}')


def get_shop_list(user):
    """Получить список покупок"""
    count_ingredients = {}
    shop_list = io.StringIO()
    writer = csv.writer(shop_list)
    writer.writerow(['Ингредиент', 'Количество'])
    ingredients = (IngredientInRecipe.objects.filter(
        ingredient__in=ShoppingList.objects.filter(user=user).values_list(
            'recipes__ingredients__id', flat=True)).values(
        'ingredient__name').annotate(total_amount=Sum('amount')))
    for item in ingredients:
        count_ingredients[item['ingredient__name']] = item['total_amount']
    for key, value in count_ingredients.items():
        writer.writerow([key, value])
    shop_list.seek(0)
    return shop_list
