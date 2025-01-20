from django import forms
from accounts .models import CustomUser


class DoctorProfileForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'profile_picture', 'specialization']

        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your username',
                'id': 'username',
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your email',
                'id': 'email',
            }),
            'profile_picture': forms.ClearableFileInput(attrs={
                'class': 'form-control',
                'id': 'profile_picture',
            }),
            'specialization': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your specialization',
                'id': 'specialization',
            }),
        }

        labels = {
            'username': 'Username',
            'email': 'Email Address',
            'profile_picture': 'Profile Picture',
            'specialization': 'Specialization',
        }
