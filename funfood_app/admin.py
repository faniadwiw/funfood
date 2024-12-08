from django.contrib import admin
from .models import CustomUser, Recipe, Category, Review, Favorite

admin.site.register(CustomUser)
admin.site.register(Recipe)
admin.site.register(Category)
admin.site.register(Review)
admin.site.register(Favorite)