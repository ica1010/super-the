# from django.contrib import admin
# from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
# from .models import User  # Importe ton modèle personnalisé

# # class UserAdmin(BaseUserAdmin):
# #     list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'is_staff')
# #     search_fields = ('username', 'email', 'first_name', 'last_name', 'role')
# #     list_filter = ('role', 'is_staff', 'is_superuser', 'is_active')
# #     ordering = ('username',)

# #     # Ajouter le champ 'role' aux sections modifiables
# #     fieldsets = (
# #         (None, {'fields': ('username', 'password')}),
# #         ('Informations personnelles', {'fields': ('first_name', 'last_name', 'email')}),
# #         ('Rôles et Permissions', {'fields': ('role', 'is_staff', 'is_active', 'is_superuser', 'groups', 'user_permissions')}),
# #         ('Dates importantes', {'fields': ('last_login', 'date_joined')}),
# #     )

# #     add_fieldsets = (
# #         (None, {
# #             'classes': ('wide',),
# #             'fields': ('username', 'password1', 'password2', 'email', 'role'),
# #         }),
# #     )

# admin.site.register(User)  # Enregistre ton modèle personnalisé

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User
from .forms import CustomUserCreationForm

class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('telephone', 'nom', 'prenoms', 'role'),
        }),
    )
    fieldsets = (
        (None, {'fields': ('telephone', 'nom', 'prenoms', 'role', 'disponible')}),
    )
    list_display = ('telephone', 'nom', 'prenoms', 'role', 'disponible')
    search_fields = ('telephone', 'nom', 'prenoms')
    ordering = ('telephone',)

admin.site.register(User, CustomUserAdmin)

