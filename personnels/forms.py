from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.core.exceptions import ValidationError
from .models import User
import random
import string

def generate_random_password(length=10):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('telephone', 'nom', 'prenoms', 'role')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['telephone'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Numéro de téléphone'})
        self.fields['nom'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Nom'})
        self.fields['prenoms'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Prénoms'})
        self.fields['password1'].widget.attrs.update({'class': 'form-control pass-input '})
        self.fields['password2'].widget.attrs.update({'class': 'form-control pass-input '})
        self.fields['role'].widget.attrs.update({'class': 'form-control'})

    def clean_telephone(self):
        telephone = self.cleaned_data.get('telephone')
        if User.objects.filter(telephone=telephone).exists():
            raise ValidationError("Ce numéro de téléphone est déjà utilisé.")
        return telephone

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data['telephone']
        user.set_password(generate_random_password())  # Génère un mot de passe sécurisé
        if commit:
            user.save()
        return user


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = ('nom', 'prenoms', 'telephone', 'role')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['telephone'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Numéro de téléphone'})
        self.fields['nom'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Nom'})
        self.fields['prenoms'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Prénoms'})
        self.fields['role'].widget.attrs.update({'class': 'form-control'})
