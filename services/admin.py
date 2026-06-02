from django.contrib import admin
from .models import UserProfile, Category, Area, Service, Review

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'phone', 'location')
    list_filter = ('role', 'created_at')
    search_fields = ('user__username', 'phone', 'location')

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Area)
class AreaAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('title', 'provider', 'category', 'price', 'availability_type', 'is_active')
    list_filter = ('is_active', 'availability_type', 'category', 'created_at')
    search_fields = ('title', 'description', 'provider__username')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('service', 'reviewer', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('service__title', 'reviewer__username')
    readonly_fields = ('created_at', 'updated_at')
