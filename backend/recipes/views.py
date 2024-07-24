from datetime import timezone
from rest_framework.exceptions import NotFound
from django.shortcuts import render
from djoser.serializers import UserSerializer
from rest_framework import viewsets, permissions
from rest_framework.exceptions import PermissionDenied
from djoser import views as djoser_views
from .models import Recipe, Tag, Ingredient, IngredientInRecipe, User  # , User
from .serializers import (RecipeSerializer, TagSerializer,
                          IngredientSerializer, IngredientInRecipeSerializer, UserMeRoleSerializer, )


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


from .filterset import RecipeFilter
from .permissions import IsAdmin, IsAdminOrReadOnly, IsModerator
#########

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = PageNumberPagination
    permission_classes = (IsAdmin,)
    http_method_names = ['get', 'post', 'patch', 'delete']
    lookup_field = 'username'
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username',)

    @action(
        methods=('GET', 'PATCH'),
        detail=False,
        permission_classes=(IsAuthenticated,),
    )
    def me(self, request):
        if request.method == 'GET':
            serializer = UserSerializer(request.user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        elif request.method == 'PATCH':
            serializer = UserMeRoleSerializer(
                request.user,
                data=request.data,
                partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data,
                            status=status.HTTP_200_OK)


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

class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (IsModerator,)

class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (IsAdminOrReadOnly,)


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (IsAdminOrReadOnly,)


class IngredientInRecipeViewSet(viewsets.ModelViewSet):
    queryset = IngredientInRecipe.objects.all()
    serializer_class = IngredientInRecipeSerializer
    permission_classes = (IsModerator,)