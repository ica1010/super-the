from django.urls import path
from . import views


urlpatterns = [
    path('create-user/', views.create_user_view, name='create-user'),
    path('edit-user/<id>', views.edit_user, name='user-edit-modal'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
]
