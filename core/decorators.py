from django.core.exceptions import PermissionDenied
from functools import wraps

from django.shortcuts import redirect

def user_is_role(required_role):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                raise PermissionDenied  # L'utilisateur n'est pas connecté
            if request.user.role != required_role:
                raise PermissionDenied  # L'utilisateur n'a pas le bon rôle
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator

# def redirect_based_on_role(view_func):
#     def _wrapped_view(request, *args, **kwargs):
#         if not request.user.is_authenticated:
#             return redirect('login')  # Redirige vers la page de connexion

#         # Vérifie le rôle de l'utilisateur et redirige vers la page appropriée
#         if request.user.role == 'ADMIN':
#             if request.path != '/admin-dashboard/':  # Remplace par l'URL correcte
#                 return redirect('admin-dashboard')
#         elif request.user.role == 'CASHIER':
#             if request.path != '/cashier-dashboard/':  # Remplace par l'URL correcte
#                 return redirect('cashier-dashboard')
#         elif request.user.role == 'WAITER':
#             if request.path != '/waiter-dashboard/':  # Remplace par l'URL correcte
#                 return redirect('waiter-dashboard')

#         return view_func(request, *args, **kwargs)  # Appelle la vue originale
#     return _wrapped_view
