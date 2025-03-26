from django.urls import reverse_lazy
from django.views.generic.edit import CreateView
from .forms import UserCreationForm
from .models import User
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import Permission
from django.shortcuts import render, get_object_or_404, redirect

class UserCreateView(CreateView):
    model = User
    form_class = UserCreationForm
    template_name = 'auth/create_user.html'
    success_url = reverse_lazy('/')  # Redirige après la création
    
    
def login_view(request):
    if request.user.is_authenticated:
        return redirect('/')
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            return redirect('dashboard')  # Redirige vers le tableau de bord
        else:
            messages.error(request, 'Identifiants invalides. Veuillez réessayer.')

    return render(request, 'auth/login.html')


@login_required(login_url='login')
def logout_view(request):
    logout(request)
    return redirect('login')



def manage_permissions(request, user_id):
    user = get_object_or_404(User, id=user_id)
    all_permissions = Permission.objects.all()
    user_permissions = user.user_permissions.all()
    content_types = ContentType.objects.all()
    permissions_data = []

    for content_type in content_types:
        permissions = Permission.objects.filter(content_type=content_type)
        if permissions.exists():
            permissions_data.append({
                "module": content_type.model.capitalize(),
                "permissions": {
                    "create": permissions.filter(codename__startswith="add").exists(),
                    "edit": permissions.filter(codename__startswith="change").exists(),
                    "delete": permissions.filter(codename__startswith="delete").exists(),
                    "view": permissions.filter(codename__startswith="view").exists(),
                }
            })
    if request.method == "POST":
        # Récupérer les permissions envoyées via le formulaire
        selected_permissions_ids = request.POST.getlist('permissions')  # Liste des IDs des permissions sélectionnées
        # Supprimer les valeurs vides (cela permet d'éviter les problèmes avec les champs vides)
        selected_permissions_ids = [p for p in selected_permissions_ids if p]

        # Si la liste de permissions sélectionnées n'est pas vide, appliquer les permissions
        if selected_permissions_ids:
            selected_permissions = Permission.objects.filter(id__in=selected_permissions_ids)
            user.user_permissions.set(selected_permissions)  # Appliquer les permissions sélectionnées
            messages.success(request, f'Les permissions de {user.username} ont été modifiées avec succès.')
        else:
            messages.error(request, 'Aucune permission sélectionnée.')

        return redirect('user-list')  # Rediriger après la mise à jour

    return render(request, 'pages/permissions.html', {
        'user': user,
        'all_permissions': all_permissions,
        'user_permissions': user_permissions,
        "permissions_data": permissions_data
    })