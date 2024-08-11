from django.contrib import admin

from .models import (Tag, Recipe, Ingredient, IngredientInRecipe, ApiUser,
                     Subscription)

admin.site.register(Recipe)
admin.site.register(Tag)
admin.site.register(Ingredient)
admin.site.register(IngredientInRecipe)
admin.site.register(ApiUser)
admin.site.register(Subscription)
