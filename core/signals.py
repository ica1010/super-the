from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.utils import timezone
from crm.models import Fournisseur, Client
from pos.models import Caisse,Order, OrderItem, Product
from notifications.signals import notify
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password

@receiver(post_save, sender=get_user_model())
def set_default_password(sender, instance, created, **kwargs):
    if created:  # Vérifie si l'utilisateur est nouvellement créé
        # Définir le mot de passe par défaut ici
        default_password = instance.telephone # Remplacez par votre mot de passe par défaut
        instance.password = make_password(default_password)
        instance.username = instance.telephone
        instance.save()
        
#Notification en temps réel aux cuisiniers lorsqu'une commande est validée
@receiver(post_save, sender=Order)
def notify_cooks_on_order_save(sender, instance, created, **kwargs):
    if instance.status == 'Validé':
        channel_layer = get_channel_layer()
        group_name = 'user-notifications'
        event = {
            'type': 'send_notifications',
            "message": f"{instance.server} vient d'etre valider une nouvelle commande"
        }
        async_to_sync(channel_layer.group_send)(group_name, event)

@receiver(post_save, sender=Order)
def ajouter_a_la_caisse_si_paye(sender, instance, **kwargs):
    if instance.status_de_paiement == 'soldée':
        # On récupère ou crée la caisse liée à l'utilisateur de la commande
        caisse, created = Caisse.objects.get_or_create(user=instance.server)
        # Ajouter le montant total de la commande à la caisse
        caisse.ajouter_entree(float(instance.get_total()))  # float pour éviter les erreurs de type
        
    
@receiver(post_save, sender=Order)
def ajouter_a_la_caisse_si_commander(sender, instance, **kwargs):
    if instance.status_de_paiement == 'soldée':
        # On récupère ou crée la caisse liée à l'utilisateur de la commande
        caisse, created = Caisse.objects.get_or_create(user=instance.server)
        # Ajouter le montant total de la commande à la caisse
        caisse.ajouter_entree(float(instance.get_total()))  # float pour éviter les erreurs de type


# Retirer le montant de la caisse si la commande est retournée
@receiver(post_save, sender=Order)
def retirer_de_caisse_si_retournee(sender, instance, **kwargs):
    if instance.status == 'Retournée' and instance.status_de_paiement == 'soldée':
        # On récupère ou crée la caisse liée à l'utilisateur de la commande
        caisse, created = Caisse.objects.get_or_create(user=instance.server)
        # Retirer le montant total de la commande de la caisse
        caisse.ajouter_sortie(float(instance.get_total())) 
        


@receiver(post_save, sender=Fournisseur)
def update_fournisseur_dette(sender, instance, created, **kwargs):
    if created:
        instance.dette = int(instance.ancienne_dette())
        instance.save(update_fields=['dette'])
        
        

# Met à jour le montant restant et montants payés lors de la création de la commande
@receiver(post_save, sender=Order)
def update_montant_restant(sender, instance, created, **kwargs):
    if created:
        instance.montant_restant = int(instance.get_total())
        instance.save(update_fields=['montant_restant'])
        client = Client.objects.get(id=instance.client.id)
        client.dette += instance.montant_restant
        client.save(update_fields=['dette'])
