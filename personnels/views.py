from django.urls import reverse_lazy
from django.views.generic.edit import CreateView
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import Permission
from .models import User
from .forms import CustomUserChangeForm, CustomUserCreationForm
from django.contrib.auth.forms import SetPasswordForm

@login_required(login_url='login')
def create_user_view(request):
    form = CustomUserCreationForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            try:
                user = form.save()
                messages.success(request, f"Utilisateur « {user.username} » créé avec succès.")
                return redirect('user-list')
            except Exception as e:
                messages.error(request, f"Erreur inattendue : {e}")
        else:
            # on détaille les erreurs champ par champ
            for field, errs in form.errors.items():
                for err in errs:
                    messages.error(request, f"{field} : {err}")
    # si on arrive ici, c’est qu’on a des erreurs → on ré-affiche la liste + la modal ouverte
    users = User.objects.all()
    return redirect('user-list')

    

@login_required(login_url='login')
def edit_user(request, id):
    user = get_object_or_404(User, id=id)

    if request.method == 'POST':
        # Mise à jour des informations utilisateur
        user.telephone = request.POST.get('telephone', user.telephone)
        user.nom = request.POST.get('nom', user.nom)
        user.prenoms = request.POST.get('prenoms', user.prenoms)
        user.role = request.POST.get('role', user.role)

        # Mise à jour du mot de passe si fourni
        new_password = request.POST.get('password', '')
        password_confirm = request.POST.get('password_confirm', '')

        if new_password and new_password == password_confirm:
            user.set_password(new_password)

        # Sauvegarde des changements
        user.save()

        # Message de succès
        messages.success(request, f'Utilisateur {user.nom} modifié avec succès !')

        # Redirection vers la liste des utilisateurs
        return redirect('user-list')  # Remplace 'user-list' par l'URL de ta liste

    return redirect('user-list')  # Remplace 'user-list' par l'URL de ta liste
 
    
def login_view(request):
    if request.user.is_authenticated:
        return redirect('/')
    try:
        if request.method == 'POST':
            username = request.POST.get('username', '').strip()
            password = request.POST.get('password', '').strip()

            # Vérifie que les champs ne sont pas vides
            if not username or not password:
                messages.warning(request, "Veuillez renseigner à la fois le nom d'utilisateur et le mot de passe.")
                return render(request, 'auth/login.html')

            # Tente d'authentifier l'utilisateur
            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                messages.success(request, f"Bienvenue {user.get_full_name() or user.username} !")
                return redirect('/')  # Redirige vers la page d'accueil ou dashboard
            else:
                messages.error(request, 'Nom d’utilisateur ou mot de passe invalide.')

    except Exception as e:
        # Logiquement tu peux logger l'erreur aussi ici pour le debug
        messages.error(request, f"Une erreur inattendue s'est produite : {str(e)}")

    return render(request, 'auth/login.html')

@login_required(login_url='login')
def logout_view(request):
    logout(request)
    return redirect('login')

