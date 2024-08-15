from datetime import timezone
from rest_framework.exceptions import NotFound
from django.shortcuts import render
# from djoser.serializers import ApiUserSerializer
from rest_framework import viewsets, permissions
from rest_framework.exceptions import PermissionDenied
from djoser import views as djoser_views
from .models import Recipe, Tag, Ingredient, IngredientInRecipe, ApiUser, Subscription
from .serializers import (
    RecipeSerializer, TagSerializer, ApiUserSerializer, IngredientSerializer,
    # IngredientInRecipeSerializer,
    # SubscriptionSerializer
)

from djoser.views import UserViewSet
from uuid import uuid4

from django.contrib.auth.tokens import default_token_generator
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, mixins, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken

from .filterset import IngredientFilter, RecipeFilter
from .permissions import IsAdmin, IsAdminOrReadOnly, IsModerator, MixedPermission, CreateUpdateDestroyDS


class ApiUserViewSet(UserViewSet):
    queryset = ApiUser.objects.all()
    serializer_class = ApiUserSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [IsModerator()]
        return super().get_permissions()

    @action(
        detail=True,
        methods=["post", "delete"],
        permission_classes=[IsAuthenticated]
    )
    def subscribe(self, request, **kwargs):
        user = request.user
        author_id = self.kwargs.get("id")
        author = get_object_or_404(ApiUser, id=author_id)

        if request.method == "POST":
            serializer = SubscriptionSerializer(
                author, data=request.data, context={"request": request}
            )
            serializer.is_valid(raise_exception=True)
            Subscription.objects.create(user=user, author=author)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == "DELETE":
            subscription = get_object_or_404(
                Subscription, user=user, author=author)
            subscription.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        permission_classes=[IsAuthenticated]
    )
    def subscriptions(self, request):
        user = request.user
        queryset = ApiUser.objects.filter(subscribing__user=user)
        pages = self.paginate_queryset(queryset)
        serializer = SubscriptionSerializer(
            pages, many=True, context={"request": request})
        return self.get_paginated_response(serializer.data)



    # permission_classes = (AllowAny,)
    # http_method_names = ['get', 'post', 'patch', 'delete']
    # lookup_field = 'username'
    # filter_backends = (filters.SearchFilter,)
    # search_fields = ('username',)

    # def get_serializer_class(self):
    #     # Если запрошенное действие (action) — получение списка объектов ('list')
    #     if self.action == 'list':
    #         # ...то применяем CatListSerializer
    #         return ApiUserSerializer
    #     # А если запрошенное действие — не 'list', применяем CatSerializer
    #     return UserCreateSerializer

    # @action(
    #     methods=('GET'),
    #     detail=False, #True - 1 object, False - list objects
    #     permission_classes=(IsAdminOrReadOnly,),
    # )
    #
    #
    # def me(self, request):
    #     if request.method == 'GET':
    #         serializer = ApiUserSerializer(request.user)
    #         return Response(serializer.data, status=status.HTTP_200_OK)
    #     elif request.method == 'PATCH':
    #         serializer = UserMeRoleSerializer(
    #             request.user,
    #             data=request.data,
    #             partial=True
    #         )
    #         serializer.is_valid(raise_exception=True)
    #         serializer.save()
    #         return Response(serializer.data,
    #                         status=status.HTTP_200_OK)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny,)
    filterset_class = IngredientFilter
    filter_backends = (DjangoFilterBackend,)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (IsModerator,)






# class IngredientInRecipeViewSet(viewsets.ModelViewSet):
#     queryset = IngredientInRecipe.objects.all()
#     serializer_class = IngredientInRecipeSerializer
#     permission_classes = (IsModerator,)



# class RecipeViewSet(viewsets.ModelViewSet):
#     queryset = Recipe.objects.all()
#     serializer_class = RecipeSerializer
#     permission_classes = (IsAdminOrReadOnly,)
#
#     http_method_names = ['get', 'post', 'patch', 'delete']
#
#     def get_queryset(self):
#         recipe_id = self.kwargs.get('recipe_id')
#         recipe = get_object_or_404(Recipe, id=recipe_id)
#         return recipe.reviews.all()
#
#     def perform_create(self, serializer):
#         recipe_id = self.kwargs.get('recipe_id')
#         recipe = get_object_or_404(Recipe, id=recipe_id)
#         serializer.save(author=self.request.user, title=recipe)


