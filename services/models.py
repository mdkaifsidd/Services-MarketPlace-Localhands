from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models.signals import post_migrate, post_save
from django.dispatch import receiver

class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('provider', 'Service Provider'),
        ('seeker', 'Service Seeker'),
        ('both', 'Both'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='seeker')
    bio = models.TextField(blank=True)
    phone = models.CharField(max_length=15, blank=True)
    profile_image = models.ImageField(upload_to='profiles/', null=True, blank=True)
    location = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()}"

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if not created:
        return
    default_role = 'both' if instance.is_staff or instance.is_superuser else 'seeker'
    UserProfile.objects.get_or_create(user=instance, defaults={'role': default_role})

@receiver(post_migrate)
def ensure_user_profiles_after_migrate(sender, **kwargs):
    if getattr(sender, 'label', None) != 'services':
        return
    for user in User.objects.all().only('id', 'is_staff', 'is_superuser'):
        default_role = 'both' if user.is_staff or user.is_superuser else 'seeker'
        UserProfile.objects.get_or_create(user=user, defaults={'role': default_role})


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    
    class Meta:
        verbose_name_plural = "Categories"
    
    def __str__(self):
        return self.name


class Area(models.Model):
    name = models.CharField(max_length=100, unique=True)
    
    class Meta:
        verbose_name_plural = "Areas"
    
    def __str__(self):
        return self.name


class Service(models.Model):
    AVAILABILITY_CHOICES = [
        ('online', 'Online Only'),
        ('offline', 'Offline Only'),
        ('both', 'Both Online & Offline'),
    ]
    PRICE_UNIT_CHOICES = [
        ('hour', 'Per Hour'),
        ('week', 'Per Week'),
        ('month', 'Per Month'),
        ('session', 'Whole Session'),
    ]
    
    provider = models.ForeignKey(User, on_delete=models.CASCADE, related_name='services')
    title = models.CharField(max_length=200)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    price_unit = models.CharField(max_length=10, choices=PRICE_UNIT_CHOICES, default='hour')
    availability_type = models.CharField(max_length=10, choices=AVAILABILITY_CHOICES)
    area = models.ForeignKey(Area, on_delete=models.SET_NULL, null=True, blank=True)
    image = models.ImageField(upload_to='services/', null=True, blank=True)
    phone = models.CharField(max_length=15, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
    
    @property
    def average_rating(self):
        reviews = self.reviews.all()
        if reviews:
            return sum([r.rating for r in reviews]) / len(reviews)
        return 0
    
    @property
    def review_count(self):
        return self.reviews.count()


class Review(models.Model):
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='reviews')
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        unique_together = ['service', 'reviewer']
    
    def __str__(self):
        return f"{self.reviewer.username} - {self.service.title} ({self.rating}★)"
