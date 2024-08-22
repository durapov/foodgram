from django.contrib import admin

from .models import (Favorite, Ingredient, IngredientInRecipe, Recipe,
                     ShoppingList, Subscribe, Tag, User)

admin.site.register(Recipe)
admin.site.register(Tag)
admin.site.register(Ingredient)
admin.site.register(IngredientInRecipe)
admin.site.register(User)
admin.site.register(Subscribe)
admin.site.register(Favorite)
admin.site.register(ShoppingList)
