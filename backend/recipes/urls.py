from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (IngredientViewSet, RecipeViewSet, TagViewSet, UserViewSet,
                    IngredientInRecipeViewSet)

v1_router = DefaultRouter()

v1_router.register('users', UserViewSet)
v1_router.register('recipes', RecipeViewSet)
v1_router.register('tags', TagViewSet)
v1_router.register('ingredients', IngredientViewSet)
v1_router.register('ingredients_recipes', IngredientInRecipeViewSet)

urlpatterns = [
    path('', include(v1_router.urls)),
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
