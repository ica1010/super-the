from django import forms
from django.contrib.auth.forms import UserCreationForm,UserChangeForm
from .models import User  # Modèle utilisateur personnalisé
from django.core.exceptions import ValidationError

class CustomUserCreationForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('telephone', 'nom', 'prenoms', 'address', 'role')

    def clean_telephone(self):
        telephone = self.cleaned_data.get('telephone')
        if User.objects.filter(telephone=telephone).exists():
            raise ValidationError("Ce numéro de téléphone est déjà utilisé.")
        return telephone

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data['telephone']
        user.set_password('default_password')  # Mot de passe par défaut
        if commit:
            user.save()
        return user
    
class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = ('nom', 'prenoms', 'telephone', 'address', 'role')
