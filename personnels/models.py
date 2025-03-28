from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import User

from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = [
        ('ADMIN', 'Administrateur'),
        ('CASHIER', 'Caissier'),
        ('WAITER', 'Serveur'),
    ]
    nom = models.CharField(max_length=50,)
    prenoms = models.CharField(max_length=50 ,)
    telephone = models.CharField(max_length=50 ,)
    address = models.CharField(max_length=50 ,)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    disponible = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
