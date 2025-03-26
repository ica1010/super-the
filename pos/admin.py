from django.contrib import admin
from unfold.admin import ModelAdmin
from django.contrib import admin
from .models import Category, Order, OrderItem, Product
from unfold.admin import ModelAdmin
from unfold.admin import TabularInline
from pos.models import Caisse, CaisseGenerale, CaisseHistorique



# Register your models here.
# admin.site.register(Reapprovisionnement)
# admin.site.register(ReapprovisionnementItem)
admin.site.register(Caisse)
class CaisseAdmin(ModelAdmin):
    # list_display = ('__all__',)
    pass

admin.site.register(CaisseGenerale)
class CaisseGeneraleAdmin(ModelAdmin):
    # list_display = ('__all__',)
    pass

admin.site.register(CaisseHistorique)
class CaisseHistoriqueAdmin(ModelAdmin):
    # list_display = ('__all__',)
    pass

class OrderItemInline(TabularInline):  # Utilise un affichage en tableau pour les objets liés
    model = OrderItem
    extra = 1  # Nombre de lignes supplémentaires vides

class OrderAdmin(ModelAdmin):
    list_display = ('id', 'server', 'created_at', 'status','status_de_paiement')
    inlines = [OrderItemInline]  # Affiche les OrderItems sur la page de commande

admin.site.register(Order, OrderAdmin)

admin.site.register(Product, ModelAdmin)
admin.site.register(Category,ModelAdmin)