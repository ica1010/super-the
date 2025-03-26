from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View
from personnels.models import User
from crm.admin import ClientForm,fournisseurForm
from .models import Client, Fournisseur, RemboursementClient, RemboursementFournisseur
from django.contrib.auth import get_user_model
from personnels.forms import CustomUserChangeForm, CustomUserCreationForm
from django.contrib.auth.models import Permission

User = get_user_model()

class UserListView(View):
    def get(self, request):
        users = User.objects.all()
        form = CustomUserCreationForm()
        all_permissions = Permission.objects.all()
        return render(request, 'pages/personnels-list.html', {'users': users, 'form': form,'all_permissions': all_permissions, })

    def post(self, request):
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            if request.htmx:  # Vérifiez si la requête provient de HTMX
                users = User.objects.all()
                return render(request, 'partials/personnels-list.html', {'users': users})
            return redirect('user-list')  # Redirection si ce n'est pas une requête HTMX

        users = User.objects.all()  # Recharge les utilisateurs pour l'affichage des erreurs
        return render(request, 'pages/personnels-list.html', {'form': form, 'users': users})

class UserDeleteView(View):
    def post(self, request, user_id):
        user = get_object_or_404(User, id=user_id)
        user_permissions = user.user_permissions.all()
        all_permissions = Permission.objects.all()
        user.delete()
        if request.htmx:  # Vérifiez si la requête provient de HTMX
            users = User.objects.all()
            return render(request, 'partials/personnels-list.html', {'users': users, 'all_permissions': all_permissions, })
        return redirect('user-list')

class UserUpdateView(View):
    def post(self, request, user_id):
        user = get_object_or_404(User, id=user_id)
        all_permissions = Permission.objects.all()
        user_permissions = user.user_permissions.all()
        form = CustomUserChangeForm(request.POST, instance=user)
        
        if form.is_valid():
            form.save()
            if request.htmx:  # Vérifiez si la requête provient de HTMX
                users = User.objects.all()
                return render(request, 'partials/personnels-list.html', {'users': users, 'all_permissions': all_permissions,'user_permissions': user_permissions,} )
            return redirect('user-list')  # Redirection si ce n'est pas une requête HTMX

        # Si le formulaire n'est pas valide, vous pouvez renvoyer les erreurs
        return render(request, 'pages/personnels-list.html', {'form': form, 'users': User.objects.all()})
def ClientList(request):
    clients = Client.objects.filter(disponible=True)
    form = ClientForm()
    
    context = {
        'clients': clients,
        'form': form,
    }
    
    return render(request, 'pages/clients-list.html', context)



def CorbeilleclientList(request):
    clients = Client.objects.filter(disponible=False)
    form = ClientForm(request.POST, request.FILES)
    
    context = {
        'clients': clients,
        'form': form,
    }
    
    return render(request, 'pages/delete-clients-list.html', context)


def AddClient(request):
    if request.method == 'POST':
        form = ClientForm(request.POST)
        print('ccccccc', form)
        try:
            form.is_valid()
            client = form.save()
            print('ccccccc', client)
        except Exception as e:
            print('erreur:',e)
    else:
        form = ClientForm()

    # Si la requête n'est pas POST, renvoyer une partie de page par défaut, en mode modal
    return redirect('client-list')


# def DeleteClient(request,id):
#     client = Client.objects.get(id=id)
#     client.delete()
#     clients = Client.objects.all()
    
#     context ={
#         'clients':clients
#     }
#     if request.headers.get('HX-Request'):
#         return render(request, 'partials/clients-list.html', {'clients': clients})
    
#     return render(request, 'pages/clients-list.html',context)

def DeleteClient(request, id):
    if request.method == 'GET':
    # Retrieve fournisseur by ID
        client = get_object_or_404(Client, id=id)
        client.disponible = not client.disponible
        client.save()
        
        
    return redirect('client-list')


def update_client_info(request, id):
    # Retrieve fournisseur by ID
    client = get_object_or_404(Client, id=id)
    
    # Check if the request is a POST request (to update data)
    if request.method == 'POST':
        name = request.POST.get('nom', client.nom)
        address = request.POST.get('address', client.adresse)
        phone_number = request.POST.get('telephone', client.telephone)
        ancienne_dette = request.POST.get('ancienne_dette', client.ancienne_dette)
        
        # Update the client's information
        client.nom = name
        client.adresse = address
        client.telephone = phone_number
        client.ancienne_dette = ancienne_dette
        client.save()
        
        # Optionally, return a success response
    return redirect('client-list')



# Create your views here.
def FournisseurList(request):
    fournisseurs = Fournisseur.objects.filter(disponible=True)
    form = fournisseurForm(request.POST, request.FILES)
    
    context = {
        'fournisseurs': fournisseurs,
        'form': form,
    }
    
    return render(request, 'pages/fournisseurs-list.html', context)

def CorbeilleFournisseurList(request):
    fournisseurs = Fournisseur.objects.filter(disponible=False)
    form = fournisseurForm(request.POST, request.FILES)
    
    context = {
        'fournisseurs': fournisseurs,
        'form': form,
    }
    
    return render(request, 'pages/delete-fournisseurs-list.html', context)

def AddFournisseur(request):
    if request.method == 'POST':
        form = fournisseurForm(request.POST, request.FILES)
        print('ccccccc', form)
        try:
            form.is_valid()
            fournisseur = form.save()
            print('ccccccc', fournisseur)
        except Exception as e:
            print('erreur:',e)
    else:
        form = fournisseurForm(request.POST, request.FILES)

    # Si la requête n'est pas POST, renvoyer 
    # une partie de page par défaut, en mode modal
    return redirect('fournisseur-list')

def rembourser_fournisseur(request, id, montant):
    """Rembourse un fournisseur en mettant à jour sa dette."""
    fournisseur = get_object_or_404(Fournisseur, id=id)
    
    # Vérifiez si le montant dépasse la dette actuelle
    if montant > fournisseur.dette:
        return HttpResponse("Le montant du remboursement dépasse la dette du fournisseur.", status=400)

    # Créer un nouvel enregistrement de remboursement
    remboursement = RemboursementFournisseur(fournisseur=fournisseur, montant=montant)
    remboursement.save()

    # Mettre à jour la dette du fournisseur
    fournisseur.dette = float(fournisseur.dette) - montant
    fournisseur.save(update_fields=["dette"])

    # Redirection ou réponse après le remboursement
    return redirect("fournisseur-list")  

def RemboursementList(request):
    remboursements = RemboursementFournisseur.objects.all()

    
    context = {
        'remboursements': remboursements,
    }
    
    return render(request, 'pages/reboursements-list.html', context)


def RemboursementClientList(request):
    remboursements = RemboursementClient.objects.all()

    
    context = {
        'remboursements': remboursements,
    }
    
    return render(request, 'pages/reboursements-client-list.html', context)

def fournir_une_vue_de_remboursement(request, id):
    """Vue pour rembourser un fournisseur."""
    fournisseur = get_object_or_404(Fournisseur, id=id)

    if request.method == "POST":
        montant = request.POST.get("montant")
        fournisseur.rembourser_dette(float(montant))
        
        return redirect('fournisseur-list')
    return redirect('fournisseur-list')

def reboursement_client(request, id):
    """Vue pour rembourser un fournisseur."""
    client = get_object_or_404(Client, id=id)

    if request.method == "POST":
        montant = request.POST.get("montant")
        try :
            client.rembourser_dette(float(montant))
            remboursement = RemboursementClient(client=client, montant=montant)
            remboursement.save()
        except Exception as e :
            return(e)
        return redirect('client-list')

    return redirect('client-list')


def update_fournisseur_info(request, id):
    # Retrieve fournisseur by ID
    fournisseur = get_object_or_404(Fournisseur, id=id)
    
    # Check if the request is a POST request (to update data)
    if request.method == 'POST':
        name = request.POST.get('nom', fournisseur.nom)
        logo = request.FILES.get('logo', fournisseur.logo)
        address = request.POST.get('address', fournisseur.adresse)
        phone_number = request.POST.get('telephone', fournisseur.telephone)
        ancienne_dette = request.POST.get('ancienne_dette', fournisseur.ancienne_dette)
        
        # Update the fournisseur's information
        fournisseur.nom = name
        fournisseur.logo = logo
        fournisseur.adresse = address
        fournisseur.telephone = phone_number
        fournisseur.ancienne_dette = ancienne_dette
        fournisseur.save()
        
        # Optionally, return a success response
    return redirect('fournisseur-list')



def DeleteFournisseur(request, id):
    if request.method == 'GET':
    # Retrieve fournisseur by ID
        fournisseur = get_object_or_404(Fournisseur, id=id)
        fournisseur.disponible = not fournisseur.disponible
        fournisseur.save()
        
        
    return redirect('fournisseur-list')

