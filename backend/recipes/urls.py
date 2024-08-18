from django.urls import include, path, re_path
from rest_framework.routers import DefaultRouter

from .views import (get_recipe_short_link, IngredientViewSet,
                    RecipeViewSet, TagViewSet, UserViewSet)

v1_router = DefaultRouter()

v1_router.register('users', UserViewSet)
v1_router.register('recipes', RecipeViewSet)
v1_router.register('tags', TagViewSet)
v1_router.register('ingredients', IngredientViewSet)

urlpatterns = [
    path('', include(v1_router.urls)),
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
    re_path(r'^s/(?P<short_link>[а-яёА-ЯЁa-z-]+)/$', get_recipe_short_link),
]
