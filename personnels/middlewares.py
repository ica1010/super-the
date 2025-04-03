from django.shortcuts import redirect
from django.utils.deprecation import MiddlewareMixin

class RestrictCashierMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.user.is_authenticated and request.user.role == 'CASHIER':
            allowed_paths = [
                '/commandes/',      # Page autorisée pour les caissiers
                '/auth/login/',      # Logout autorisé
                '/auth/logout/',      # Logout autorisé
            ]
            if request.path.startswith('/static/') or request.path.startswith('/media/'):
                return None  # Autorise l'accès aux fichiers statiques et médias

            if request.path not in allowed_paths:
                return redirect('/commandes/')  # Redirige vers la page commandes
