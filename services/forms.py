from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import UserProfile, Service, Review

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    role = forms.ChoiceField(choices=UserProfile.ROLE_CHOICES)
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2', 'role')
    
    def save(self, commit=True):
        user = super().save(commit=commit)
        if not commit:
            return user
        role = self.cleaned_data.get('role')
        UserProfile.objects.update_or_create(user=user, defaults={'role': role})
        return user


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['bio', 'phone', 'profile_image', 'location']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4}),
            'phone': forms.TextInput(attrs={'type': 'tel'}),
        }


class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = ['title', 'category', 'description', 'price', 'price_unit', 'availability_type', 'area', 'image', 'phone']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 5}),
            'title': forms.TextInput(attrs={'placeholder': 'Service Title'}),
            'price': forms.NumberInput(attrs={'step': '0.01'}),
            'phone': forms.TextInput(attrs={'type': 'tel'}),
        }


class ReviewForm(forms.ModelForm):
    RATING_CHOICES = [(i, f'{i} ★') for i in range(1, 6)]
    rating = forms.TypedChoiceField(choices=RATING_CHOICES, coerce=int, widget=forms.RadioSelect)

    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'comment': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Share your experience...'}),
        }
