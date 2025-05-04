from datetime import timedelta
from decimal import Decimal
from personnels.models import User
from crm.models import Fournisseur
from django.db import models, transaction
from django.db.models import Sum, F
from django.utils import timezone
from djmoney.models.fields import MoneyField
from measurement.measures import Mass
from django_measurement.models import MeasurementField
from django.contrib.auth.models import Permission
from djmoney.money import Money
from django.utils.timezone import now
from django.db.models import Max

UNIT_CHOICES = [
    ("Litre", "Litre"),
    ("Unité", "Unité"),
]

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
    
    
    add_at = models.DateField(auto_created=True, auto_now_add=True)
    update_at = models.DateField(auto_now=True)
    class Meta:
        ordering = ['-add_at'] 
    def __str__(self):
        return self.name


class productSize(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='sizes')
    size = models.CharField(max_length=100,blank=True, null=True, default='Grand')
    price = MoneyField(
        max_digits=14, 
        decimal_places=0, 
        default_currency='XOF'
    )

    def __str__(self):
        return f"{self.product.name} : {self.size} - {self.price}"

class Ingredient(models.Model):
    name = models.CharField(max_length=100)
    price = MoneyField(max_digits=14, decimal_places=0, default_currency='XOF', blank=True, null=True)
    quantity = models.FloatField(blank=True, null=True)
    unit = models.CharField(max_length=10, choices=UNIT_CHOICES, default="Litre")
    entry_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class ProductIngredient(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="ingredients")
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE, related_name="products")
    quantity_required = models.FloatField(blank=True, null=True)
    unit = models.CharField(max_length=10, choices=UNIT_CHOICES, default="l")

    def __str__(self):
        return f"{self.quantity_required} {self.unit} de {self.ingredient.name} pour {self.product.name}"

class StockMovement(models.Model):
    MOUVEMENT_TYPE = [
        ('Entrée', 'Entrée'),
        ('Sortie', 'Sortie'),
    ]
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="stock_movements", null=True, blank=True)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE, related_name="stock_movements", null=True, blank=True)
    unit_price = MoneyField(max_digits=14, decimal_places=0, default_currency='XOF', blank=True, null=True)
    amount_paid = MoneyField(max_digits=14, decimal_places=0, default_currency='XOF', blank=True, null=True)
    fournisseur = models.ForeignKey(Fournisseur, on_delete=models.CASCADE, related_name="stock_movements", null=True, blank=True)
    quantity_used = models.FloatField(blank=True, null=True)
    quantity = models.FloatField(blank=True, null=True)
    unit = models.CharField(max_length=10, choices=UNIT_CHOICES, default="l")
    movement_date = models.DateTimeField(auto_now_add=True)
    description = models.TextField(blank=True, null=True)
    type_de_mouvement = models.CharField(max_length=20, choices=MOUVEMENT_TYPE, default='Sortie')
    decaisement = models.BooleanField(default=True)


    def consume_ingredient(self, product_ingredient):
        remaining_qty = product_ingredient.quantity_required
        stock_entries = Ingredient.objects.filter(id=product_ingredient.ingredient.id, quantity__gt=0).order_by("entry_date")
        for entry in stock_entries:
            if remaining_qty <= 0:
                break
            if entry.quantity >= remaining_qty:
                entry.quantity -= remaining_qty
                entry.save()
                remaining_qty = 0
            else:
                remaining_qty -= entry.quantity
                entry.quantity = 0
                entry.save()

    @property
    def total_amount(self):
        """ Calcule le montant total = quantité * prix unitaire """
        if self.unit_price and self.quantity:
            return self.unit_price * self.quantity
        return Money(0, 'XOF')

    @property
    def remaining_amount(self):
        """ Calcule le reste à payer = montant total - montant payé """
        return self.total_amount - (self.amount_paid or Money(0, 'XOF'))
    def __str__(self):
        return f"Stock Movement for {self.product.name if self.product else self.ingredient.name}"

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
    relicat = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    montant_remise = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    status_de_payement = models.CharField(max_length=50, blank=True)
    daily_sequence = models.PositiveIntegerField(null=True, blank=True)
    validated_at = models.DateTimeField(null=True, blank=True, auto_now=True)
    
    add_at = models.DateTimeField(auto_now_add=True)
    change_at = models.DateTimeField(auto_now=True)


    def save(self, *args, **kwargs):
        if self.daily_sequence is None:
            today = now().date()

            # Récupérer la dernière valeur de la séquence pour aujourd'hui
            last_sequence = (
                Order.objects.filter(created_at__date=today)
                .aggregate(Max('daily_sequence'))['daily_sequence__max'] or 0
            )

            self.daily_sequence = last_sequence + 1

        # Optionnel : génère une référence avec la séquence
        """    if not self.reference:
        today_str = now().strftime('%Y%m%d')
        self.reference = f"{today_str}-{self.daily_sequence:04d}"""

        super().save(*args, **kwargs)

    def __str__(self):
        return f"Order {self.id} - {self.get_status_display()}"


    def total_items_count(self):
        return sum(item.quantity for item in self.items.all())


    def get_total(self):
        """Calculates total of all items in the order."""
        return sum(item.get_total() for item in self.items.all())


    def register_partial_payment(self, amount):
        """Handles partial payments for the order."""
        amount = Decimal(amount)  # Convertit le montant en un type Decimal pour des calculs précis avec des nombres décimaux.

        if not self.client:
            raise ValueError("La commande n'a pas de client associé.")

        if not self.get_total() > int(amount) :  # Vérifie si le montant du paiement partiel ne dépasse pas le montant restant dû.
                self.montant_remise = amount  # Augmente le montant payé par le montant du paiement partiel.
                self.relicat = int(amount) - self.get_total()  # Réduit la dette du client par le montant du paiement.
                self.save()  # Sauvegarde l'état mis à jour de la commande.
        else:
            raise ValueError("Sols insufisant.")  # Si le montant est supérieur au montant restant, une erreur est levée.

   
    def consume_ingredients(self):
          pass
    def _update_stock(self, ingredient, quantity_needed):
        """ Réduit le stock de l'ingrédient en fonction du FIFO """
        stock_entries = Ingredient.objects.filter(id=ingredient.id, quantity__gt=0).order_by("entry_date")

        for entry in stock_entries:
            if quantity_needed <= 0:
                break
            if entry.quantity >= quantity_needed:
                entry.quantity -= quantity_needed
                entry.save()
                quantity_needed = 0
            else:
                quantity_needed -= entry.quantity
                entry.quantity = 0
                entry.save()


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    # product = models.ForeignKey(Product, on_delete=models.CASCADE, blank=True, null=True)
    size = models.ForeignKey(productSize, on_delete=models.CASCADE, blank=True, null=True)
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
        return self.custom_product_price.amount or self.size.price.amount

    def get_total(self):
        """Calculates total price for the item."""
        return self.size.price.amount * self.quantity





    # def __str__(self):
    #     return f"{self.size.product.name} (x{self.quantity})"

    def save(self, *args, **kwargs):
        """Saves the item and updates the order's total."""
        if not self.custom_product_name:
            self.custom_product_name = self.size.product.name
        if self.custom_product_price is None:
            self.custom_product_price = self.size.product.price
        super().save(*args, **kwargs)
       

class Depense(models.Model):
    name = models.CharField(("nom de la depense"), max_length=150)
    date = models.DateTimeField(("Date de la depense"), auto_now_add=True)
    note = models.TextField(("ajouter une note a la depense"),blank=True, null=True)
    justification = models.FileField(("ajouter une piece jointe pour justifier  la depense"), upload_to=None, max_length=100)
    amount = MoneyField(("Montant payé"), max_digits=12,  decimal_places=0, default_currency="XOF")
    in_cash = models.BooleanField(("prende l'argent dans la caisse ?"), default=True)
    
    delete = models.BooleanField(("Supprimer la depense"), default=False)
    def __str__(self):
        return self.name
    
    
    
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
