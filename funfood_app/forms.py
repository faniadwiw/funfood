from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from .models import CustomUser

class CustomAuthenticationForm(AuthenticationForm):
    username = forms.CharField(label='Username atau Email', widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    def clean(self):
        username = self.cleaned_data.get('username')
        if '@' in username:
            try:
                user = CustomUser.objects.get(email=username)
                self.cleaned_data['username'] = user.username
            except CustomUser.DoesNotExist:
                raise forms.ValidationError('Email atau password salah.')
        return super().clean()

class CustomUserCreationForm(UserCreationForm):
    nickname = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    phone_number = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    profile_image = forms.ImageField(required=False, widget=forms.FileInput(attrs={'class': 'form-control'}))

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'nickname', 'phone_number', 'profile_image', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }