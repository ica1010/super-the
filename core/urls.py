from django.contrib import admin
from django.urls import path
from . import views
urlpatterns = [
    path('', views.Dashboard, name='dashboard'),
    path('commandes/', views.VendorDashboard, name='vendor-dashboard'),
    path('achat/', views.Achat, name='achat'),
    path('cuisine/', views.Cuisinier, name='cuisinier'),
    path('payement/<int:order_id>/', views.payement, name='payement'),
    path('total-orders/<str:status>/', views.get_total_orders_by_status, name='get_total_orders_by_status'),
    path('get-order-data/', views.get_order_data, name='get_order_data'),

]