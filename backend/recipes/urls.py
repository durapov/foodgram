from django.urls import include, path, re_path
from djoser.views import UserViewSet
from rest_framework.routers import DefaultRouter

from .views import (RecipeViewSet, TagViewSet, ApiUserViewSet, IngredientViewSet,)

v1_router = DefaultRouter()

v1_router.register('users', ApiUserViewSet)
v1_router.register('recipes', RecipeViewSet)
v1_router.register('tags', TagViewSet)
v1_router.register('ingredients', IngredientViewSet)

urlpatterns = [
    path('', include(v1_router.urls)),
    path('', include('djoser.urls')),
    re_path(r'^auth/', include('djoser.urls.authtoken')),
]


# v1_router.register('users',
#                    ApiUserViewSet, basename='users')
# v1_router.register(r'users/subscriptions',
#                    ApiUserViewSet, basename='subscriptions')
# v1_router.register(r'users/(?P<user_id>\d+)/subscribe',
#                    ApiUserViewSet, basename='subscribe')
# v1_router.register('recipes',
#                    RecipeViewSet, basename='recipes')
# v1_router.register('recipes/download_shopping_cart/',
#                    RecipeViewSet, basename='shopping_cart')
# v1_router.register(r'recipes/(?P<recipe_id>\d+)/shopping_cart',
#                    RecipeViewSet, basename='recipe_shopping_cart')
# v1_router.register(r'recipes/(?P<recipe_id>\d+)/favorite',
#                    RecipeViewSet, basename='favorite')
# v1_router.register('tags', TagViewSet)
#v1_router.register(r'tags/(?P<tag_id>\d+)/', TagViewSet, basename='tag-detail')
# v1_router.register('ingredients', IngredientViewSet, basename='ingredients')