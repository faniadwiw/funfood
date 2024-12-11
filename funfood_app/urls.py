from django.urls import path
from . import views

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('about/', views.AboutView.as_view(), name='about'),
    path('recipe/<int:pk>/', views.RecipeDetailView.as_view(), name='recipe_detail'),
    
    # auth
    path('login/', views.login_view , name='login'),
    path('register/', views.register_view , name='register'),
    path('logout/', views.logout_view , name='logout'),
    
    # user
    path('recipes/my/', views.MyRecipesView.as_view(), name='my_recipes'),
    path('recipe/add/', views.RecipeCreateView.as_view(), name='add_recipe'),
    path('recipe/edit/<int:pk>/', views.RecipeUpdateView.as_view(), name='edit_recipe'),
    path('recipe/delete/<int:pk>/', views.RecipeDeleteView.as_view(), name='delete_recipe'),
    path('recipe/<int:pk>/review/', views.add_review, name='add_review'),
    path('recipe/favorites/', views.FavoriteRecipesView.as_view(), name='favorite_recipes'),
    path('recipe/<int:pk>/favorite/', views.toggle_favorite, name='toggle_favorite'),
    
    # admin
    path('a/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('a/recipes/', views.admin_recipes, name='admin_recipes'),
    path('a/categories/', views.admin_categories, name='admin_categories'),
    path('a/users/', views.admin_users, name='admin_users'),
    path('a/recipe/<int:pk>/approve/', views.admin_approve_recipe, name='admin_approve_recipe'),
]
