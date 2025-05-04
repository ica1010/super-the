from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import Category, Depense, Ingredient, Order, OrderItem, Product, ProductIngredient, StockMovement, productSize
from unfold.admin import TabularInline
from pos.models import Caisse, CaisseGenerale, CaisseHistorique
from django.contrib.admin import register


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
    list_display = ('id', 'server', 'client', 'get_total','status','status_de_paiement','created_at')
    inlines = [OrderItemInline]  # Affiche les OrderItems sur la page de commande

admin.site.register(Order, OrderAdmin)

admin.site.register(Product, ModelAdmin)
admin.site.register(productSize, ModelAdmin)
admin.site.register(Category,ModelAdmin)
admin.site.register(Depense, ModelAdmin)


@register(Ingredient)
class IngredientAdmin(ModelAdmin):
    list_display = ('name', 'price', 'quantity',  'entry_date')
    search_fields = ('name',)
    list_filter = ('entry_date',)

@register(ProductIngredient)
class ProductIngredientAdmin(ModelAdmin):
    list_display = ('product', 'ingredient', 'quantity_required')
    search_fields = ('product__name', 'ingredient__name')

@register(StockMovement)
class StockMovementAdmin(ModelAdmin):
    list_display = ('product', 'ingredient', 'quantity_used', 'movement_date')
    list_filter = ('movement_date',)
    search_fields = ('product__name', 'ingredient__name')