from django.contrib import admin

from .models import Tag, Recipe, Ingredient, IngredientInRecipe, User

admin.site.register(Recipe)
admin.site.register(Tag)
admin.site.register(Ingredient)
admin.site.register(IngredientInRecipe)
admin.site.register(User)