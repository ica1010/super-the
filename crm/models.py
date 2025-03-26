from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
from decimal import Decimal
# Create your models here.
class Fournisseur(models.Model):
    logo = models.ImageField(upload_to='logo', default='fournieur_logo.png')
    nom = models.CharField(max_length=255)
    telephone = PhoneNumberField(blank=True)
    adresse = models.TextField()
    dette = models.DecimalField(max_digits=10, decimal_places=2, blank=True, default=0)
    ancienne_dette =models.DecimalField(max_digits=10, decimal_places=2, blank=True, default=0)
    date_ajout = models.DateTimeField(auto_now_add=True)
    disponible = models.BooleanField(default=True)
    
    def __str__(self):
        return self.nom
    
    def ajouter_dette(self, montant):
        """Ajoute un montant à la dette actuelle du fournisseur."""
        if montant > 0:
            self.dette += Decimal(montant)
            self.save()

    def rembourser_dette(self, montant):
        """Diminue la dette actuelle du fournisseur en fonction du montant remboursé."""
        if montant > 0:
            montant = Decimal(montant)
            if montant >= self.dette:
                self.ancienne_dette += self.dette
                self.dette = 0
            else:
                self.dette -= montant
            self.save()

class Client(models.Model):
    nom = models.CharField(max_length=255)
    telephone = PhoneNumberField(blank=True)
    adresse = models.TextField()
    ancienne_dette =models.DecimalField(max_digits=10, decimal_places=2, blank=True, default=0)
    dette = models.DecimalField(max_digits=10, decimal_places=2, blank=True, default=0)
    date_ajout = models.DateTimeField(auto_now_add=True)
    disponible = models.BooleanField(default=True)

    def __str__(self):
        return self.nom
    
    def ajouter_dette(self, montant):
        """Ajoute un montant à la dette actuelle du client."""
        if montant > 0:
            self.dette += Decimal(montant)
            self.save()

    def rembourser_dette(self, montant):
        """Diminue la dette actuelle du client en fonction du montant remboursé."""
        if montant > 0:
            montant = Decimal(montant)
            if montant >= self.dette:
                self.ancienne_dette += self.dette
                self.dette = 0
            else:
                self.dette -= montant
            self.save()
           
           
# class Remboursement(models.Model):
#     client = models.ForeignKey(Client, on_delete=models.CASCADE)
#     montant = models.DecimalField(max_digits=10, decimal_places=2)
#     date = models.DateTimeField(auto_now_add=True)
#     order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True)  # Relier à une commande spécifique

#     def __str__(self):
#         return f"{self.client} - {self.montant} - {self.date}"
    
class RemboursementFournisseur(models.Model):
    fournisseur = models.ForeignKey(Fournisseur, on_delete=models.CASCADE)
    montant = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Remboursement {self.montant} à {self.fournisseur} le {self.date}"
    
    
class RemboursementClient(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    montant = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.client} a remboursé {self.montant} Franc Cfa le {self.date}"