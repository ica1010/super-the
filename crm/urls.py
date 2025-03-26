from django.contrib import admin
from django.urls import path
from . import views
urlpatterns = [
    path('list-des-clients', views.ClientList, name='client-list'),
    path('rebourser-le-client/<id>', views.reboursement_client, name='reboursement-client'),
    path('supprimé-le-client/<id>', views.DeleteClient, name='delete-client'),
    path('modifié-le-client/<id>', views.update_client_info, name='update-client'),
    path('list-des-client-suprimé', views.CorbeilleclientList, name='client-deleted'),
    path('nouveau-client/', views.AddClient, name='nouveau-client'),
    
    
    path('personnels/', views.UserListView.as_view(), name='user-list'),
     path('users/delete/<int:user_id>/', views.UserDeleteView.as_view(), name='user-delete'),
    path('users/update/<int:user_id>/', views.UserUpdateView.as_view(), name='user-update'),
    
    
    path('list-des-remboursement', views.RemboursementList, name='remboursement-list'),
    path('list-des-remboursement-des-clients', views.RemboursementClientList, name='remboursement-client-list'),
    
    
    
    path('list-des-fournisseur', views.FournisseurList, name='fournisseur-list'),
    path('list-des-fournisseur-suprimé', views.CorbeilleFournisseurList, name='fournisseur-deleted'),
    path('rebourser-le-fournisseur/<id>', views.fournir_une_vue_de_remboursement, name='rembourser-fournisseur'),
    path('supprimé-le-fournisseur/<id>', views.DeleteFournisseur, name='delete-fournisseur'),
    path('modifié-le-fournisseur/<id>', views.update_fournisseur_info, name='update-fournisseur'),
    path('nouveau-fournisseur/', views.AddFournisseur, name='nouveau-fournisseur'),


] 