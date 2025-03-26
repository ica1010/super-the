from django.urls import path
from . import views


urlpatterns = [
    path('create-user/', views.UserCreateView.as_view(), name='create-user'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('permission/<user_id>', views.manage_permissions, name='manage-permissions'),
]
