from datetime import timedelta
from decimal import Decimal
from personnels.models import User
from crm.models import Fournisseur
from django.db import models, transaction
from django.db.models import Sum, F
from django.utils import timezone
from djmoney.models.fields import MoneyField
from django.contrib.auth.models import Permission


class Category(models.Model):
    image = models.ImageField(upload_to='category', default='img.jpeg')
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='category', default='img.jpeg')
    code = models.CharField(max_length=100, unique=True, blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    price = MoneyField(
        max_digits=14, 
        decimal_places=0, 
        default_currency='XOF'
    )
    
    add_at = models.DateField(auto_created=True, auto_now_add=True)
    update_at = models.DateField(auto_now=True)
    class Meta:
        ordering = ['-add_at'] 
    def __str__(self):
        return self.name

class Order(models.Model):

    STATUS_CHOICES = [
        ('En cours', 'En cours'),
        ('Validé', 'Validé'),
        ('Retournée', 'Retournée'),
        ('Annulé', 'Annulé'),
        ('Mis en pause', 'Mis en pause'),
    ]

    PAYMENT_STATUS_CHOICES = [
        ('soldée', 'soldée'),
        ('non soldée', 'non soldée'),
    ]

    def get_default_client():
        from crm.models import Client
        try:
            return Client.objects.get(nom='default')
        except Client.DoesNotExist:
            return None

    server = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, limit_choices_to={'role': 'WAITER'}, related_name='commandes')
    client = models.ForeignKey("crm.Client", on_delete=models.SET_NULL, null=True, default=get_default_client)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='En cours')
    status_de_paiement = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='non soldée')
    montant_restant = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    montant_paye = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    status_de_payement = models.CharField(max_length=50, blank=True)
    validated_at = models.DateTimeField(null=True, blank=True, auto_now=True)
    add_at = models.DateTimeField(auto_now_add=True)
    change_at = models.DateTimeField(auto_now=True)
    delete = models.BooleanField(default=False)

    def __str__(self):
        return f"Order {self.id} - {self.get_status_display()}"


    # @transaction.atomic
    # def save(self, *args, **kwargs):
    #     if self.status == 'En cours':
    #         Order.objects.filter(status='En cours', server=self.server).update(status='Mis en pause')

    #     if self.montant_restant < 1 :
    #         Order.objects.filter(status_de_paiement='soldée')

    #     super(Order, self).save(*args, **kwargs)

    def get_total(self):
        """Calculates total of all items in the order."""
        return sum(item.get_total() for item in self.items.all())

    # def update_amounts(self):
    #     """Updates remaining amount and payment status."""
    #     total = self.get_total()
    #     self.montant_restant = total - self.montant_paye
    #     Caisse
    #     self.status_de_paiement = 'soldée' if self.montant_restant == 0 else 'non soldée'
    #     self.save()

    def register_partial_payment(self, amount):
        """Handles partial payments for the order."""
        amount = Decimal(amount)  # Convertit le montant en un type Decimal pour des calculs précis avec des nombres décimaux.

        if not self.client:
            raise ValueError("La commande n'a pas de client associé.")

        if amount <= self.montant_restant:  # Vérifie si le montant du paiement partiel ne dépasse pas le montant restant dû.
            if self.client.dette >= amount:  # Vérifie si la dette du client est suffisante pour le paiement.
                self.montant_paye = self.montant_paye + amount  # Augmente le montant payé par le montant du paiement partiel.
                self.montant_restant = self.montant_restant - amount  # Réduit le montant restant dû par le montant du paiement.
                self.client.dette = self.client.dette - amount  # Réduit la dette du client par le montant du paiement.
                self.update_amounts()  # Met à jour les montants, probablement pour recalculer ou ajuster d'autres valeurs.
                self.client.save()  # Sauvegarde l'état mis à jour du client.
                self.save()  # Sauvegarde l'état mis à jour de la commande.
            else:
                raise ValueError("Le montant dépasse la dette du client.")  # Si le montant est supérieur à la dette, une erreur est levée.
        else:
            raise ValueError("Le montant est supérieur au solde restant.")  # Si le montant est supérieur au montant restant, une erreur est levée.

    def total_remise(self):
        total_discount_value = 0
        total_discount_percentage = 0

        # Pour chaque item dans la commande
        for item in self.items.all():
            discount_info = item.remise()
            total_discount_value += discount_info['discount_value']
            # Le pourcentage de remise globale est plus complexe à calculer en cumulé
            # ici on somme juste les pourcentages de remise individuels
            total_discount_percentage += discount_info['discount_percentage']

        return {
            'total_discount_value': total_discount_value,
            'total_discount_percentage': total_discount_percentage
        }


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    custom_product_name = models.CharField(max_length=255, blank=True)
    custom_product_price =  MoneyField(
        max_digits=14, 
        decimal_places=0, 
        default_currency='XOF', default=0.00
    )
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} x {self.get_product_name()} (Commande {self.order.id})"

    def get_product_name(self):
        """Returns custom name or product name."""
        return self.custom_product_name or self.product.name

    def get_product_price(self):
        """Returns custom price or product price."""
        return self.custom_product_price.amount or self.product.price.amount

    def get_total(self):
        """Calculates total price for the item."""
        return self.get_product_price() * self.quantity

    def remise(self):
        # Suppose the Product model has a 'price' field
        product_price = self.product.price  # Original product price
        custom_price = self.custom_product_price  # Custom price, if any

        if custom_price:  # If there's a custom price, calculate the discount
            discount = product_price - custom_price
            try :
                discount_percentage = (discount / product_price) * 100
            except ZeroDivisionError:
                return {
                    'discount_value': 0,
                    'discount_percentage': 0
                }
            return {
                'discount_value': discount,
                'discount_percentage': discount_percentage
            }
        return {
            'discount_value': 0,
            'discount_percentage': 0
        }




    def __str__(self):
        return f"{self.product.name} (x{self.quantity})"

    def save(self, *args, **kwargs):
        """Saves the item and updates the order's total."""
        if not self.custom_product_name:
            self.custom_product_name = self.product.name
        if self.custom_product_price is None:
            self.custom_product_price = self.product.price
        super().save(*args, **kwargs)
        # self.order.update_amounts()
        self.order.save(update_fields=['montant_restant', 'status_de_paiement'])


class Caisse(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    solde_initial = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    solde_actuel = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total_entrees = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_sorties = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    date_ouverture = models.DateTimeField(auto_now_add=True)
    date_fermeture = models.DateTimeField(null=True, blank=True)
    is_cloture = models.BooleanField(default=False)

    def cloturer(self):
        self.is_cloture = True
        self.date_fermeture = timezone.now()
        self.save()
        # Enregistrement de l'état de la caisse dans l'historique
        CaisseHistorique.objects.create(
            caisse=self,
            solde_final=self.solde_actuel,
            date_cloture=self.date_fermeture
        )

    def ajouter_entree(self, montant):
        # Vérifiez d'abord si montant est un int ou un float
        if not isinstance(montant, (int, float)):
            print("heeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee")
            raise ValueError("Le montant doit être un nombre (int ou float)")

        # Convertissez ensuite le montant en Decimal
        montant = Decimal(montant)

        # Ajoutez le montant aux totaux
        self.total_entrees += montant
        self.solde_actuel += montant
        self.save()

    def ajouter_sortie(self, montant):
        montant = Decimal(montant)
        if self.solde_actuel >= montant:
            self.total_sorties += montant
            self.solde_actuel -= montant
            self.save()
        else:
            raise ValueError("Le solde de la caisse est insuffisant pour ce décaissement.")

    def __str__(self):
        return f"Caisse de {self.user}"

class CaisseHistorique(models.Model):
    caisse = models.ForeignKey(Caisse, on_delete=models.CASCADE, related_name='historiques')
    solde_final = models.DecimalField(max_digits=10, decimal_places=2)
    date_cloture = models.DateTimeField()
    user_cloture = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"Historique de la caisse - {self.date_cloture}"

class CaisseGenerale(models.Model):
    solde_total = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    dernier_mise_a_jour = models.DateTimeField(auto_now=True)

    def mettre_a_jour_solde(self):
        self.solde_total = sum(caisse.solde_actuel for caisse in Caisse.objects.filter(is_cloture=False))
        self.save()

    def __str__(self):
        return f"Caisse Générale - Solde: {self.solde_total} Franc CFA"
