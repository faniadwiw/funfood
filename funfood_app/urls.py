from django.urls import path
from . import views

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('recipe/<int:pk>/', views.RecipeDetailView.as_view(), name='recipe_detail'),
    
    # auth
    path('login/', views.login_view , name='login'),
    path('register/', views.register_view , name='register'),
    path('logout/', views.logout_view , name='logout'),
]
