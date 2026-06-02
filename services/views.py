from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.contrib import messages
from django.db.models import Q
from .models import Service, UserProfile, Review, Category, Area
from .forms import UserRegistrationForm, UserProfileForm, ServiceForm, ReviewForm


def get_or_create_profile(user):
    profile, _ = UserProfile.objects.get_or_create(
        user=user,
        defaults={'role': 'both' if user.is_staff or user.is_superuser else 'seeker'},
    )
    return profile


def vite_client(request):
    return HttpResponse('', content_type='application/javascript')

def favicon(request):
    return HttpResponse(status=204)


def home(request):
    services = Service.objects.filter(is_active=True)[:6]
    categories = Category.objects.all()
    total_services = Service.objects.filter(is_active=True).count()
    total_providers = User.objects.filter(profile__role__in=['provider', 'both']).count()
    
    context = {
        'services': services,
        'categories': categories,
        'total_services': total_services,
        'total_providers': total_providers,
    }
    return render(request, 'home.html', context)


def register(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Account created successfully! Please log in.')
            return redirect('login')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            get_or_create_profile(user)
            messages.success(request, f'Welcome back, {user.username}!')
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'login.html')


def logout_view(request):
    logout(request)
    messages.success(request, 'Logged out successfully.')
    return redirect('home')


@login_required
def dashboard(request):
    profile = get_or_create_profile(request.user)
    context = {'profile': profile}
    
    if profile.role in ['provider', 'both']:
        services = Service.objects.filter(provider=request.user)
        context['services'] = services
    
    return render(request, 'dashboard.html', context)


@login_required
def edit_profile(request):
    profile = get_or_create_profile(request.user)
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('dashboard')
    else:
        form = UserProfileForm(instance=profile)
    
    return render(request, 'edit_profile.html', {'form': form})


@login_required
def service_list(request):
    services = Service.objects.filter(is_active=True)
    category = request.GET.get('category')
    area = request.GET.get('area')
    search = request.GET.get('search')
    availability = request.GET.get('availability')
    
    if category:
        services = services.filter(category__id=category)
    if area:
        services = services.filter(area__id=area)
    if search:
        services = services.filter(Q(title__icontains=search) | Q(description__icontains=search))
    if availability:
        services = services.filter(availability_type=availability)
    
    categories = Category.objects.all()
    areas = Area.objects.all()
    
    context = {
        'services': services,
        'categories': categories,
        'areas': areas,
        'selected_category': category,
        'selected_area': area,
        'search_query': search,
    }
    return render(request, 'services/service_list.html', context)


@login_required
def service_detail(request, pk):
    service = get_object_or_404(Service, pk=pk, is_active=True)
    reviews = service.reviews.all()
    user_review = None
    
    user_review = reviews.filter(reviewer=request.user).first()
    
    context = {
        'service': service,
        'reviews': reviews,
        'user_review': user_review,
        'average_rating': service.average_rating,
    }
    return render(request, 'services/service_detail.html', context)


@login_required
def create_service(request):
    profile = get_or_create_profile(request.user)
    if profile.role not in ['provider', 'both']:
        messages.error(request, 'Only service providers can create services.')
        return redirect('home')
    
    if request.method == 'POST':
        form = ServiceForm(request.POST, request.FILES)
        if form.is_valid():
            service = form.save(commit=False)
            service.provider = request.user
            service.save()
            messages.success(request, 'Service created successfully!')
            return redirect('my_services')
    else:
        form = ServiceForm()
    
    return render(request, 'services/service_form.html', {'form': form, 'title': 'Create Service'})


@login_required
def edit_service(request, pk):
    service = get_object_or_404(Service, pk=pk, provider=request.user)
    
    if request.method == 'POST':
        form = ServiceForm(request.POST, request.FILES, instance=service)
        if form.is_valid():
            form.save()
            messages.success(request, 'Service updated successfully!')
            return redirect('my_services')
    else:
        form = ServiceForm(instance=service)
    
    return render(request, 'services/service_form.html', {'form': form, 'title': 'Edit Service', 'service': service})


@login_required
def delete_service(request, pk):
    service = get_object_or_404(Service, pk=pk, provider=request.user)
    if request.method == 'POST':
        service.delete()
        messages.success(request, 'Service deleted successfully!')
    return redirect('my_services')


@login_required
def my_services(request):
    profile = get_or_create_profile(request.user)
    if profile.role not in ['provider', 'both']:
        messages.error(request, 'Only service providers can access this page.')
        return redirect('home')
    
    services = Service.objects.filter(provider=request.user)
    context = {'services': services}
    return render(request, 'services/my_services.html', context)


@login_required
def add_review(request, service_id):
    service = get_object_or_404(Service, pk=service_id, is_active=True)
    existing_review = service.reviews.filter(reviewer=request.user).first()
    
    if request.method == 'POST':
        form = ReviewForm(request.POST, instance=existing_review)
        if form.is_valid():
            review = form.save(commit=False)
            review.service = service
            review.reviewer = request.user
            review.save()
            messages.success(request, 'Review posted successfully!')
            return redirect('service_detail', pk=service.pk)
    else:
        form = ReviewForm(instance=existing_review)
    
    context = {
        'form': form,
        'service': service,
        'is_edit': existing_review is not None,
    }
    return render(request, 'reviews/add_review.html', context)


@login_required
def delete_review(request, review_id):
    review = get_object_or_404(Review, pk=review_id, reviewer=request.user)
    service_id = review.service.id
    if request.method == 'POST':
        review.delete()
        messages.success(request, 'Review deleted.')
    return redirect('service_detail', pk=service_id)
