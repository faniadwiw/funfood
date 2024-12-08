from django.shortcuts import render
from django.views.generic import TemplateView
from .models import Recipe, Category

class HomeView(TemplateView):
    template_name = 'public/home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["latest_recipes"] = Recipe.objects.filter(is_approved=True).order_by('-created_at')[:6] 
        context["categories"] = Category.objects.all()[:6]
        return context
