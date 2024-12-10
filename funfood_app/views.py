from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import logout, authenticate, login
from django.views.generic import TemplateView, DetailView
from .models import Recipe, Category
from .forms import CustomAuthenticationForm, CustomUserCreationForm

# home
class HomeView(TemplateView):
    template_name = 'public/home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["latest_recipes"] = Recipe.objects.filter(is_approved=True).order_by('-created_at')[:6] 
        context["categories"] = Category.objects.all()[:6]
        return context

# recipe detail
class RecipeDetailView(DetailView):
    model = Recipe
    template_name = 'public/recipe_detail.html'
    context_object_name = 'recipe'
    

#------------------------------| AUTH |------------------------------
def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Selamat datang, {user.username}.')
                return redirect('home')
            
        messages.error(request, 'Username/Email atau password salah.')
    else:
        form = CustomAuthenticationForm()
    return render(request, 'auth/login.html', {'form': form})

def register_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Akun berhasil dibuat. Silahkan login.')
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'auth/register.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.success(request, 'Anda telah keluar.')
    return redirect('home')