from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from django.contrib.auth import logout, authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.admin.views.decorators import staff_member_required
from django.views.generic import TemplateView, DetailView, ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse, reverse_lazy
from django.http import HttpResponseBadRequest, HttpResponseRedirect
from .models import CustomUser, Recipe, Category, Favorite
from django.db.models import Count
from .forms import CustomAuthenticationForm, CustomUserCreationForm, ReviewForm, RecipeForm

#------------------------------| PUBLIC |------------------------------
class HomeView(TemplateView):
    template_name = 'public/home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["latest_recipes"] = Recipe.objects.filter(is_approved=True).order_by('-created_at')[:6] 
        context["categories"] = Category.objects.all()[:6]
        return context

class AboutView(TemplateView):
    template_name = 'public/about.html'

class RecipeDetailView(DetailView):
    model = Recipe
    template_name = 'public/recipe_detail.html'
    context_object_name = 'recipe'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["reviews"] = self.object.reviews.all().order_by('-created_at')
        context["review_form"] = ReviewForm()
        context["is_favorited"] = self.object.is_favorited_by(self.request.user) if self.request.user.is_authenticated else False
        return context
    

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
                if user.is_superuser:
                    return redirect('admin_dashboard')
                else:
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

    
#------------------------------| USER |------------------------------
class MyRecipesView(LoginRequiredMixin, ListView):
    model = Recipe
    template_name = 'user/my_recipes.html'
    context_object_name = 'recipes'
    
    def get_queryset(self):
        return Recipe.objects.filter(user=self.request.user).order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['form'] = RecipeForm()
        return context

class RecipeCreateView(LoginRequiredMixin, CreateView):
    model = Recipe
    form_class = RecipeForm
    template_name = 'components/modal/add_recipe.html'
    success_url = reverse_lazy('my_recipes')
    login_url = reverse_lazy('login')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        return context

    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, 'Resep berhasil ditambahkan!')
        return super().form_valid(form)

class RecipeUpdateView(LoginRequiredMixin, UpdateView):
    model = Recipe
    form_class = RecipeForm
    template_name = 'components/modal/edit_recipe.html'
    context_object_name = 'recipe'
    login_url = reverse_lazy('login')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        if self.request.method == 'GET':
            context['form'] = RecipeForm(instance=self.object)
        return context
    
    def get_success_url(self):
        messages.success(self.request, 'Resep berhasil diperbarui.')
        return reverse_lazy('my_recipes')
    
    def get_queryset(self):
        return Recipe.objects.filter(user=self.request.user)
    
class RecipeDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Recipe
    success_url = reverse_lazy('my_recipes')
    template_name = 'components/modal/delete_recipe.html'
    login_url = reverse_lazy('login')
    
    def test_func(self):
        recipe = self.get_object()
        return self.request.user == recipe.user
    
    def delete(self, request, *args, **kwargs):
        result = super().delete(request, *args, **kwargs)
        messages.success(self.request, 'Resep berhasil dihapus!')
        return result
    
    def handle_no_permission(self):
        messages.error(self.request, 'Anda tidak memiliki izin untuk menghapus resep ini.')
        return HttpResponseRedirect(self.success_url)
    
class FavoriteRecipesView(LoginRequiredMixin, ListView):
    model = Recipe
    template_name = 'user/favorite_recipes.html'
    context_object_name = 'recipes'
    login_url = reverse_lazy('login')
    
    def get_queryset(self):
        return Recipe.objects.filter(favorites__user=self.request.user).order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        return context

@login_required
def add_review(request, pk):
    recipe = get_object_or_404(Recipe, pk=pk)
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.recipe = recipe
            review.save()
            messages.success(request, 'Terima kasih atas ulasannya.')
            return redirect('recipe_detail', pk=pk)
    else:
        form = ReviewForm()
    return render(request, 'public/recipe_detail.html', {'recipe': recipe, 'review_form': form, 'reviews': recipe.reviews.all()})

@login_required
def toggle_favorite(request, pk):
    recipe = get_object_or_404(Recipe, pk=pk)
    if request.method == 'POST':
        favorite = Favorite.objects.filter(user=request.user, recipe=recipe)
        if favorite.exists():
            favorite.delete()
            messages.success(request, f'{recipe.title} dihapus dari favorit.')
        else:
            Favorite.objects.create(user=request.user, recipe=recipe)
            messages.success(request, f'{recipe.title} ditambahkan ke favorit.')
        
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', reverse('recipe_detail', kwargs={'pk': pk})))
    return HttpResponseBadRequest()


#------------------------------| ADMIN |------------------------------
@staff_member_required
def admin_dashboard(request):
    context = {
        'total_users': CustomUser.objects.count(),
        'total_recipes': Recipe.objects.count(),
        'pending_recipes': Recipe.objects.filter(is_approved=False).count(),
        'total_categories': Category.objects.count(),
        'latest_recipes': Recipe.objects.order_by('-created_at')[:5],
        'popular_categories': Category.objects.annotate(
            recipe_count=Count('recipes')).order_by('-recipe_count')[:5]
    }
    return render(request, 'admin/dashboard.html', context)

@staff_member_required
def admin_recipes(request):
    recipes = Recipe.objects.select_related('user', 'category').order_by('-created_at')

    status_filter = request.GET.get('status', 'all')

    if status_filter == 'pending':
        recipes = recipes.filter(is_approved=False)
    elif status_filter == 'approved':
        recipes = recipes.filter(is_approved=True)
        
    context = {
        'recipes': recipes,
        'status_filter': status_filter
    }
    
    return render(request, 'admin/recipes.html', context)

@staff_member_required
def admin_categories(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        if name:
            Category.objects.create(name=name, description=description)
            messages.success(request, 'Kategori berhasil ditambahkan.')
        return redirect('admin_categories')
    
    categories = Category.objects.annotate(recipe_count=Count('recipes'))
    return render(request, 'admin/categories.html', {'categories': categories})

@staff_member_required
def admin_users(request):
    users = CustomUser.objects.annotate(
        recipe_count=Count('recipes'),
        review_count=Count('reviews')
    )
    return render(request, 'admin/users.html', {'users': users})

@staff_member_required
def admin_approve_recipe(request, pk):
    recipe = get_object_or_404(Recipe, pk=pk)
    recipe.is_approved = True
    recipe.save()
    messages.success(request, f'Resep "{recipe.title}" telah disetujui.')
    return redirect('admin_recipes')