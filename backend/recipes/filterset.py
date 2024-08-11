from django_filters import rest_framework as filters

from .models import Ingredient, Recipe


class RecipeFilter(filters.FilterSet):
    genre = filters.CharFilter(field_name="genre__slug")
    category = filters.CharFilter(field_name="category__slug")

    class Meta:
        model = Recipe
        fields = '__all__'

class IngredientFilter(filters.FilterSet):
    name = filters.CharFilter(lookup_expr="startswith")

    class Meta:
        model = Ingredient
        fields = ["name"]