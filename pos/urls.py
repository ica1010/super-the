from django.contrib import admin
from django.urls import path
from . import views
urlpatterns = [
    path('list-des-ventes', views.OrdersList, name='orders-list'),
    path('list-des-ventes-supprimé', views.DeletedOrdersList, name='deleted-orders-list'),
    
    
    path('list-des-ventes-retournée', views.ReturnedOrdersList, name='return-orders-list'),
    path('cancel-order/<id>', views.CancelOrder, name='cancel-order'),
    path('detail-de-vente/<id>', views.OrderDetail, name='order-detail'),
    path('update-order/<int:order_id>/', views.update_order, name='update_order'),
    path('delete-admin-order/<int:order_id>/', views.delete_order, name='admin-delete-order'),
    
    
    path('list-des-produits', views.ProductList, name='products-list'),
    path('list-des-ingredients', views.IngredientsList, name='ingredients-list'),
    path('ingredient/nouvelle', views.ingredient_create, name='ingredient_create'),
    path('ingredient/modifier/<pk>', views.ingredient_update, name='ingredient_update'),
    path('ingredient/delete/<pk>', views.ingredient_delete, name='ingredient_delete'),
    path('ajouter-un-produits', views.add_product, name='add-product'),
    path('changer-le-produit/<int:id>', views.update_product, name='update-product'),
    path('supprimé-de-produit/<int:id>/', views.delete_product, name='delete-product'),
    
    
    path('list-des-category', views.CategoryList, name='category-list'),
    path('ajouter-une-category', views.add_Category, name='add-category'),
    path('changer-le-categorie/<int:id>', views.update_Category, name='update-category'),
    path('supprimé-de-categorie/<int:id>/', views.delete_Category, name='delete-category'),
    
     path('add-ingredient-form/', views.add_ingredient_form, name='add_ingredient_row'),
    # path('reaprovisionnement/<int:id>', views.reaprovisionnement, name='reaprovisionnement'),
    path('reaprovisionnement', views.reaprovisionnementList, name='reaprovisionnementList'),
    path('reapprovisionnement/<id>', views.reaprovisionnement, name='reaprovisionnement'),
    path('add-item-form/', views.add_item_form, name='add_item_form'),
    
    
    path('add-order/', views.add_product_to_order, name='add_product_to_order'),
    path('add-reaprovisionnement/', views.add_product_to_reapo, name='add_product_to_reapo'),
    
    
    path('add-client-on-order/', views.creer_client, name='new-clien-on-order'),
    path('add-fournisseur-on-reapovisionement/', views.creer_fournisseur, name='add-fournisseur-on-reapovisionement'),
    
    path('refresh-order/', views.refresh_order, name='refresh_order'),
    path('refresh-reapovisionement/', views.refresh_reapovisionement, name='refresh_reapovisionement'),
    
    path('delete-order-item/<int:item_id>/', views.delete_order_item, name='delete_order_item'),
    path('delete-reaprovisionement-item/<int:item_id>/', views.delete_reaprovisionement_item, name='delete_reaprovisionement_item'),
    
    path('increment-item/<int:item_id>/', views.increment_order_item, name='increment_order_item'),
    path('increment-reaprovisionement-item/<int:item_id>/', views.increment_reaprovisionement_item, name='increment_reaprovisionement_item'),
    
    path('decrement-item/<int:item_id>/', views.decrement_order_item, name='decrement_order_item'),
    path('decrement-reaprovisionement-item/<int:item_id>/', views.decrement_reaprovisionement_item, name='decrement_reaprovisionement_item'),
    
    path('update-item/<int:item_id>/', views.update_order_item, name='update_item'),
    path('update-oreaprovisionement-item/<int:item_id>/', views.update_oreaprovisionement_item, name='update_oreaprovisionement_item'),
    
    path('clear-order/<int:order_id>/', views.clear_order, name='clear-order'),
    path('cancel-current-order/<int:order_id>/', views.cancel_order, name='cancel-current-order'),
    
    
    path('delete-order/<int:order_id>/', views.delete_paused_order, name='delete-order'),
    path('save-order/<int:order_id>/', views.save_order, name='save-order'),
    
    
    path('save-reaprovisionement/<int:id>/', views.save_reaprovisionement, name='save-reaprovisionement'),
    
    
    # path('save-order/<int:order_id>/', views.save_order, name='save-order'),
    path('paused-order/<int:order_id>/', views.paused_order, name='paused-order'),
    path('unpaused-order/<int:order_id>/', views.unpause_order, name='unpaused-order'),
    path('modifier-order/<int:order_id>/', views.modify_order, name='modify-order'),
    
    path('update_payment/<int:order_id>/', views.update_payment, name='update_payment'),
    
    path('update-reaprovisionement-payment/<int:id>/', views.update_reaprovisionement_payment, name='update_reaprovisionement_payment'),
    
    path('choose-customer/<int:id>/', views.choose_customer, name='choose_customer'),
    
    path('choose-fournisseur/<int:id>/', views.choose_fournissuer, name='choose_fournissuer'),
    
    
    path('fiche-de-stock/', views.fiche_Stock, name='fiche_Stock'),
    path('depense/', views.cash_expense, name='depense'),
    path('depense/add/', views.add_expense, name='add_expense'),
    path('depense/<id>', views.update_expense, name='update_expense'),
    path('depense/<id>/delete', views.delete_expense, name='delete_expense'),
    
    
    

]