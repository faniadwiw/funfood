from django.db import models
from django.contrib.auth.models import AbstractUser

# user
class CustomUser(AbstractUser):
    nickname = models.CharField(max_length=20)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    profile_image = models.ImageField(upload_to='profile/', blank=True, null=True)
    
    @property
    def approved_recipes_count(self):
        return self.recipes.filter(approved=True).count()
    
    @property
    def avg_rating(self):
        approved_recipes = self.recipes.filter(approved=True)
        if approved_recipes.exists():
            total_rating = sum(recipe.reviews.aggregate(models.Sum('rating'))['rating__sum'] or 0 for recipe in approved_recipes)
            total_reviews = sum(recipe.reviews.count() for recipe in approved_recipes)
            return round(total_rating / total_reviews, 2) if total_reviews > 0 else 0
        return 0
    

# recipe
class Recipe(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='recipes')
    title = models.CharField(max_length=100)
    description = models.TextField()
    ingredients = models.TextField()
    steps = models.TextField()
    image = models.ImageField(upload_to='recipe/', blank=True, null=True)
    category = models.ForeignKey('Category', on_delete=models.CASCADE, related_name='recipes')
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def get_avg_rating(self):
        reviews = self.reviews.all()
        if reviews.exists():
            total_rating = sum(review.rating for review in reviews)
            return round(total_rating / reviews.count(), 2)
        return 0
    
    def __str__(self):
        return self.title
    
    
# category
class Category(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField()
    
    def __str__(self):
        return self.name


# review
class Review(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='reviews')
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveIntegerField()
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f'{self.user}\'s review on {self.recipe}'


# favorite
class Favorite(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='favorites')
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='favorites')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f'{self.user.username} - {self.recipe.title}'