from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from django.contrib.auth import logout, authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.admin.views.decorators import staff_member_required
from django.views.generic import TemplateView, DetailView, ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.core.exceptions import PermissionDenied
from django.urls import reverse, reverse_lazy
from django.http import HttpResponseBadRequest, HttpResponseRedirect
from .models import CustomUser, Recipe, Category, Favorite
from django.db.models import Count
from .forms import CustomAuthenticationForm, CustomUserCreationForm, CustomUserChangeForm, ReviewForm, RecipeForm

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
                if user.is_staff:
                    return redirect('staff_dashboard')
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


#------------------------------| STAFF |------------------------------
@staff_member_required
def staff_dashboard(request):
    context = {
        'total_recipes': Recipe.objects.count(),
        'pending_recipes': Recipe.objects.filter(is_approved=False).count(),
        'total_categories': Category.objects.count(),
        'latest_recipes': Recipe.objects.order_by('-created_at')[:5],
        'popular_categories': Category.objects.annotate(
            recipe_count=Count('recipes')).order_by('-recipe_count')[:5]
    }
    return render(request, 'staff/dashboard.html', context)

@staff_member_required
def staff_recipes(request):
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
    
    return render(request, 'staff/recipes.html', context)

@staff_member_required
def staff_approve_recipe(request, pk):
    recipe = get_object_or_404(Recipe, pk=pk)
    recipe.is_approved = True
    recipe.save()
    messages.success(request, f'Resep "{recipe.title}" telah disetujui.')
    return redirect('staff_recipes')

@staff_member_required
def staff_reject_recipe(request, pk):
    recipe = get_object_or_404(Recipe, pk=pk)
    if request.method == 'POST':
        recipe.is_approved = False
        recipe.save()
        messages.success(request, f'Resep "{recipe.title}" telah ditolak.')
    return redirect('staff_recipes')

@staff_member_required 
def staff_categories(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')

        # Check if category with same name exists
        if Category.objects.filter(name=name).exists():
            messages.error(request, f'Kategori dengan nama "{name}" sudah ada.')
        elif name:
            try:
                Category.objects.create(name=name, description=description)
                messages.success(request, 'Kategori berhasil ditambahkan.')
                return redirect('staff_categories')
            except Exception as e:
                messages.error(request, f'Gagal menambahkan kategori: {str(e)}')

        # Return with form data if validation fails
        return render(request, 'staff/categories.html', {
            'categories': Category.objects.annotate(recipe_count=Count('recipes')),
            'form_data': {'name': name, 'description': description}
        })

    categories = Category.objects.annotate(recipe_count=Count('recipes'))
    return render(request, 'staff/categories.html', {'categories': categories})

@staff_member_required
def staff_edit_category(request, pk):
    category = get_object_or_404(Category, pk=pk)
    
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')

        # Check if another category with same name exists
        if Category.objects.exclude(pk=pk).filter(name=name).exists():
            messages.error(request, f'Kategori dengan nama "{name}" sudah ada.')
        elif name:
            try:
                category.name = name
                category.description = description
                category.save()
                messages.success(request, 'Kategori berhasil diperbarui.')
                return redirect('staff_categories')
            except Exception as e:
                messages.error(request, f'Gagal memperbarui kategori: {str(e)}')
        
        return redirect('staff_categories')
        
    return redirect('staff_categories')


#------------------------------| ADMIN |------------------------------
@login_required
def admin_dashboard(request):
    if not request.user.is_superuser:
        raise PermissionDenied
    
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

@login_required
def admin_recipes(request):
    if not request.user.is_superuser:
        raise PermissionDenied
    
    recipes = Recipe.objects.select_related('user', 'category').order_by('-created_at')

    status_filter = request.GET.get('status', 'all')

    if status_filter == 'pending':
        recipes = recipes.filter(is_approved=False)
    elif status_filter == 'approved':
        recipes = recipes.filter(is_approved=True)
        
    context = {
        'recipes': recipes,
        'status_filter': status_filter,
        'users': CustomUser.objects.filter(is_superuser=False),
        'categories': Category.objects.all()
    }
    
    return render(request, 'admin/recipes.html', context)

@login_required
def admin_add_recipe(request):
    if not request.user.is_superuser:
        raise PermissionDenied
    
    if request.method == 'POST':
        form = RecipeForm(request.POST, request.FILES)
        if form.is_valid():
            recipe = form.save(commit=False)
            recipe.user_id = request.POST.get('user')
            recipe.is_approved = True
            recipe.save()
            messages.success(request, 'Resep berhasil ditambahkan.')
            return redirect('admin_recipes')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'Error pada {field}: {error}')
    return redirect('admin_recipes')

@login_required
def admin_edit_recipe(request, pk):
    if not request.user.is_superuser:
        raise PermissionDenied
    
    recipe = get_object_or_404(Recipe, pk=pk)
    
    if request.method == 'POST':
        form = RecipeForm(request.POST, request.FILES, instance=recipe)
        if form.is_valid():
            form.save()
            messages.success(request, f'Resep "{recipe.title}" berhasil diperbarui.')
            return redirect('admin_recipes')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'Error pada {field}: {error}')
    return redirect('admin_recipes')

@login_required
def admin_delete_recipe(request, pk):
    if not request.user.is_superuser:
        raise PermissionDenied
    
    recipe = get_object_or_404(Recipe, pk=pk)
    
    if request.method == 'POST':
        recipe.delete()
        messages.success(request, f'Resep "{recipe.title}" berhasil dihapus.')
        return redirect('admin_recipes')
    
    return redirect('admin_recipes')

@login_required
def admin_approve_recipe(request, pk):
    if not request.user.is_superuser:
        raise PermissionDenied
    
    recipe = get_object_or_404(Recipe, pk=pk)
    recipe.is_approved = True
    recipe.save()
    messages.success(request, f'Resep "{recipe.title}" telah disetujui.')
    return redirect('admin_recipes')

@login_required
def admin_categories(request):
    if not request.user.is_superuser:
        raise PermissionDenied
    
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        if name:
            Category.objects.create(name=name, description=description)
            messages.success(request, 'Kategori berhasil ditambahkan.')
        return redirect('admin_categories')
    
    categories = Category.objects.annotate(recipe_count=Count('recipes'))
    return render(request, 'admin/categories.html', {'categories': categories})

@login_required
def admin_users(request):
    if not request.user.is_superuser:
        raise PermissionDenied
    
    users = CustomUser.objects.annotate(
        recipe_count=Count('recipes'),
        review_count=Count('reviews')
    )
    return render(request, 'admin/users.html', {'users': users})

@login_required
def admin_add_user(request):
    if not request.user.is_superuser:
        raise PermissionDenied
    
    if request.method == 'POST':
        try:
            form = CustomUserCreationForm(request.POST, request.FILES)
            if form.is_valid():
                user = form.save(commit=False)
                user.is_staff = request.POST.get('is_staff') == 'on'
                user.is_superuser = False 
                user.save()
                messages.success(request, f'User {user.username} berhasil ditambahkan.')
                return redirect('admin_users')
            else:
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f'Error pada {field}: {error}')
        except Exception as e:
            messages.error(request, f'Gagal menambahkan user: {str(e)}')
        return redirect('admin_users')
    
    # GET requests not allowed, redirect to users list
    return redirect('admin_users')

@login_required
def admin_edit_user(request, pk):
    if not request.user.is_superuser:
        raise PermissionDenied
    
    user = get_object_or_404(CustomUser, pk=pk)
    
    if request.method == 'POST':
        form = CustomUserChangeForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, f'User {user.username} berhasil diperbarui.')
            return redirect('admin_users')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'Error pada {field}: {error}')
    else:
        form = CustomUserChangeForm(instance=user)
    
    return redirect('admin_users')

@login_required
def admin_delete_user(request, pk):
    if not request.user.is_superuser:
        raise PermissionDenied
    
    user = get_object_or_404(CustomUser, pk=pk)
    
    if request.method == 'POST':
        user.delete()
        messages.success(request, f'User {user.username} berhasil dihapus.')
        return redirect('admin_users')
    
    return redirect('admin_users')

