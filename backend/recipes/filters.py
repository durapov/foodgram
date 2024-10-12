from django_filters.rest_framework import CharFilter, FilterSet, NumberFilter

from .models import Favorite, Recipe, ShoppingList


class IngredientFilter(FilterSet):
    name = CharFilter(lookup_expr='istartswith')


class RecipeFilter(FilterSet):
    tags = CharFilter(method='filter_tags')
    author = NumberFilter(
        lookup_expr='exact',
        field_name='author'
    )
    is_favorited = NumberFilter(method='filter_is_favorited')
    is_in_shopping_cart = NumberFilter(
        method='filter_is_in_shopping_cart')

    class Meta:
        model = Recipe
        fields = ['tags', 'author', 'is_favorited', 'is_in_shopping_cart']

    def filter_tags(self, queryset, name, value):
        if not value:
            return queryset
        get_tags = [
            tag_value for tag_value in self.request.GET.getlist('tags')]
        queryset = queryset.filter(tags__slug__in=get_tags).distinct()
        return queryset

    def filter_is_favorited(self, queryset, name, value):
        if not self.request.user.is_authenticated:
            return Favorite.objects.none()
        get_favorites = Favorite.objects.filter(user=self.request.user)
        return queryset.filter(
            id__in=get_favorites.values_list('recipes_id', flat=True)
        )

    def filter_is_in_shopping_cart(self, queryset, name, value):
        if not self.request.user.is_authenticated:
            return ShoppingList.objects.none()
        get_shopping_cart = ShoppingList.objects.filter(user=self.request.user)
        return queryset.filter(
            id__in=get_shopping_cart.values_list('recipes_id', flat=True)
        )
