from django.contrib.auth.models import AbstractUser
from django.db import models
from django.contrib.auth.base_user import BaseUserManager

class CustomUserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, telephone, password, **extra_fields):
        """
        Crée et enregistre un User avec le téléphone comme identifiant.
        """
        if not telephone:
            raise ValueError('Le numéro de téléphone doit être défini')
        user = self.model(telephone=telephone, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, telephone, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(telephone, password, **extra_fields)

    def create_superuser(self, telephone, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Le superuser doit avoir is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Le superuser doit avoir is_superuser=True.')

        return self._create_user(telephone, password, **extra_fields)

class User(AbstractUser):
    # On utilise le champ "telephone" comme identifiant (username)
    objects = CustomUserManager()
    USERNAME_FIELD = 'telephone'
    # Lors de la création d'un superuser, on demandera ces champs
    REQUIRED_FIELDS = ['nom', 'prenoms', 'address', 'role']

    ROLE_CHOICES = [
        ('ADMIN', 'Administrateur'),
        ('CASHIER', 'Caissier'),
    ]
    nom = models.CharField(max_length=50)
    prenoms = models.CharField(max_length=50)
    telephone = models.CharField(max_length=50, unique=True)
    address = models.TextField("", blank=True, null=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    disponible = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.telephone} ({self.get_role_display()})"
