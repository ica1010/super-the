from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_exempt
from crm.models import Fournisseur
from pos.models import Caisse
from pos.forms import CategoryForm, DepenseAddForm, DepenseDeleteForm, DepenseUpdateForm, IngredientForm, ProductForm
from pos.models  import Category, Product
from .models import Depense, Ingredient, Order, ProductIngredient, StockMovement, productSize
from django.utils import timezone
from django.utils import timezone
from django.shortcuts import get_object_or_404, redirect, render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django import forms
from decimal import Decimal, InvalidOperation
from django.db.models import Count, Q,Sum, Max
from .models import Order, OrderItem
from pos.models import Caisse, Product
from crm.models import Client, Fournisseur
from django.contrib import messages
from django.db.models.functions import TruncHour
from django.utils.timezone import localtime
from django.db.models.functions import TruncHour
from django.db.models import Sum, Count
from datetime import timedelta
from datetime import datetime
# Create your views here.
from django.utils.timezone import localtime
from datetime import datetime, timedelta
from django.db.models import Count, Sum
from django.db.models.functions import TruncHour
from django.utils.timezone import localtime
from datetime import datetime, timedelta
from django.db.models import Count, Sum
from django.db.models.functions import TruncHour
from django.db.models import F, Sum

from datetime import datetime, timedelta
from django.db.models import Count, Sum, F
from django.db.models.functions import TruncHour
from django.utils.timezone import localtime

def OrdersList(request):
    daterange = request.GET.get('daterange')
    
    if not daterange:
        today_str = datetime.today().strftime('%Y-%m-%d')
        daterange = f"{today_str} - {today_str}"
        request.GET = request.GET.copy()
        request.GET['daterange'] = daterange

    start_str, end_str = daterange.split(' - ')
    start_date = datetime.strptime(start_str.strip(), '%Y-%m-%d')
    end_date = datetime.strptime(end_str.strip(), '%Y-%m-%d') + timedelta(days=1)

    # Toujours définir orders ici
    orders = Order.objects.filter(
        created_at__range=(start_date, end_date)
    ).exclude(items__isnull=True)

    # Calcul du total avec F()
    total_amount = OrderItem.objects.filter(order__in=orders).aggregate(
        total=Sum(F('size__price') * F('quantity'))
    )['total'] or 0

    # Statistiques par heure
    ordersc = (
        orders.annotate(hour=TruncHour('created_at'))
        .values('hour')
        .annotate(nombre_commandes=Count('id'))
        .order_by('hour')
    )

    orders_by_hour = []
    for entry in ordersc:
        hour_start = localtime(entry['hour'])
        hour_end = hour_start + timedelta(hours=1)
        orders_by_hour.append({
            'hour_start': hour_start,
            'hour_end': hour_end,
            'nombre_commandes': entry['nombre_commandes']
        })

    context = {
        'orders': orders,
        'orders_by_hour': orders_by_hour,
        'total_amount': total_amount,
        'daterange': daterange
    }

    return render(request, 'pages/orders-list.html', context)


def DeletedOrdersList(request):
    orders = Order.objects.prefetch_related('items__product').filter(delete =True)
    
    context ={
        'orders':orders
    }
    
    return render(request, 'pages/deleted-orders-list.html',context)

def ReturnedOrdersList(request):
    orders = Order.objects.prefetch_related('items__product').filter(status = 'Retournée')
    
    context ={
        'orders':orders
    }
    
    return render(request, 'pages/return-orders-list.html',context)

def OrderDetail(request, id):
    order = Order.objects.prefetch_related('items__size').get(id=id)
    
    context ={
        'order':order
    }

    return render(request, 'pages/order-detail.html',context)

def CancelOrder(request, id):
    order = Order.objects.get(id=id)
    order.status = 'Retournée'
    order.save()

    return redirect('return-orders-list')

def update_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    if request.method == 'POST':
        for item in order.items.all():
            # Récupérer la quantité et le prix personnalisé depuis le formulaire
            new_quantity = request.POST.get(f'quantity_{item.id}')
            new_custom_price = request.POST.get(f'custom_price_{item.id}')
            new_custom_name = request.POST.get(f'custom_name_{item.id}')

            # Mettre à jour la quantité si elle est fournie
            if new_quantity:
                item.quantity = int(new_quantity)
            
            if new_custom_name:
                item.custom_product_name = new_custom_name
            
            # Mettre à jour le prix personnalisé si fourni
            if new_custom_price:
                item.custom_product_price = float(new_custom_price)

            item.save()

        # Renvoyer le modal mis à jour
        html = render_to_string('partials/admin-order-update.html', {'order': order})
        return JsonResponse({'html': html})
    
def delete_order(request, order_id):
    current_order = get_object_or_404(Order, id=order_id)

    if request.method == "GET":
        # Bascule l'état de suppression de la commande
        current_order.delete = not current_order.delete
        current_order.save()
        
        # Redirige en fonction de l'état de suppression
        if request.path == '/pos/list-des-ventes':
            return redirect('orders-list')  # Redirige vers la liste des commandes supprimées
        else:
            return redirect('deleted-orders-list')
        


def add_ingredient_form(request):
    ingredients = Ingredient.objects.all()  # Récupérer les ingrédients disponibles
    return render(request, "partials/ingredient_form.html", {"ingredients": ingredients})


def ProductList(request):
    products = Product.objects.all()
    category = Category.objects.all()
    form = ProductForm()
    ingredients = Ingredient.objects.all()
    context = {
        'ingredients':ingredients,
        'products':products,
        'category':category,
        'form':form,
    }
    return render(request, 'pages/product-list.html',context)

def IngredientsList(request):
    products = Ingredient.objects.all()
    fournisseurs = Fournisseur.objects.filter(disponible=True)
    form = IngredientForm()
    context = {
        'products':products,
        'form':form,
        'fournisseurs':fournisseurs
    }
    return render(request, 'pages/ingredient-list.html',context)


def ingredient_create(request):
    if request.method == "POST":
        form = IngredientForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('ingredients-list')
    else:
        form = IngredientForm()
    return redirect('ingredients-list', {'form': form})

def ingredient_update(request, pk):
    ingredient = get_object_or_404(Ingredient, pk=pk)

    if request.method == "POST":
        name = request.POST.get("name")
        price = request.POST.get("price")
        quantity = request.POST.get("quantity")
        unit = request.POST.get("unit")

        # Mettre à jour l'objet Ingredient
        ingredient.name = name
        ingredient.price.amount = price  # Assurez-vous que price est bien un MoneyField
        ingredient.quantity = quantity
        ingredient.unit = unit

        ingredient.save()
        return redirect('ingredients-list')
    return redirect('ingredients-list')

def ingredient_delete(request, pk):
    ingredient = get_object_or_404(Ingredient, pk=pk)
    ingredient.delete()
        
    return redirect('ingredients-list')

def add_product(request):
    if request.method == 'POST':
        try:
            form = ProductForm(request.POST, request.FILES)
            sizes = request.POST.getlist("sizes[]")
            prices = request.POST.getlist("prices[]")

            if form.is_valid():
                product = form.save()  # Sauvegarde du produit
                
                for size, price in zip(sizes, prices):
                    try:
                        # Création de la relation produit-ingrédient
                        productSize.objects.create(
                            product=product,
                            size=size,
                            price=price
                        )
                    except Exception as e:
                        messages.error(request, f"erreur :{e}")
                        return redirect("add-product")

                messages.success(request, "Produit ajouté avec succès !")
                return redirect("products-list")

            else:
                messages.error(request, "Veuillez corriger les erreurs du formulaire.")
        
        except Exception as e:
            messages.error(request, f"Une erreur s'est produite : {str(e)}")

        return redirect("add-product")

    else:
        try:
            form = ProductForm()
            ingredients = Ingredient.objects.all()
            return redirect("products-list")

        except Exception as e:
            messages.error(request, f"Erreur lors du chargement du formulaire : {str(e)}")
            return redirect("products-list")

def update_product(request, id):
    product = get_object_or_404(Product, id=id)
    if request.method == 'POST':
        nom = request.POST.get('nom')
        categorie_id = request.POST.get('cat')
        code = request.POST.get('code')
        image = request.FILES.get('image')
        sizes = request.POST.getlist("sizes[]")
        prices = request.POST.getlist("prices[]")
        
        category = get_object_or_404(Category, id=categorie_id)
        if image: 
            product.image = image
            
        product.name = nom
        product.code = code
        product.category = category
        product.save()
        
        productSize.objects.filter(product=product).delete()
        for size, price in zip(sizes, prices):
                try:
                    productSize.objects.create(
                        product=product,
                        size=size,
                        price=price
                    )
                except Exception as e:
                    print(f"Erreur lors de la mise à jour des tailles : {e}")
                    messages.error(request, f"Erreur lors de la mise à jour des tailles : {e}")
                    return redirect("products-list")
            
        return redirect("products-list")

   
    return redirect("products-list")


@csrf_exempt
def delete_product(request, id):
    product = get_object_or_404(Product, id=id)
    products = Product.objects.all()
    product.delete()
    messages.success(request, f"Produit {product.name} supprimée avec succès.")
    return redirect("products-list")

def CategoryList(request):
    categories = Category.objects.all()
    form = CategoryForm()
    context = {
        'categories':categories,
        'form':form,
    }
    return render(request, 'pages/category-list.html',context)

def add_Category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            categories = Category.objects.all()
            messages.success(request, "Catégorie ajoutée avec succès !")
            return redirect("category-list")

        else:
            # Retourner des erreurs de formulaire si nécessaire
            return redirect("category-list")

    return redirect("category-list")


def update_Category(request, id):
    category = get_object_or_404(Category, id=id)
    if request.method == 'POST':
        nom = request.POST.get('nom')
        image = request.FILES.get('image')
        if nom:
            category.name = nom
        if image : 
            category.image = image
        category.save()
        messages.success(request, "Catégorie mise à jour avec succès !")
        # categories = Category.objects.all()
        return redirect("category-list")

   
    return redirect("category-list")


@csrf_exempt
def delete_Category(request, id):
    category = get_object_or_404(Category, id=id)
    category.delete()
    messages.success(request, f"Catégorie {category.name} supprimée avec succès.")
    return redirect("category-list")

def reaprovisionnement(request,id):
    
    if request.method == 'POST':
        quantity = request.POST.get('quantity')
        price = request.POST.get('price')
        amount_paid = request.POST.get('amount_paid')
        fournisseur_id = request.POST.get('fournisseur_id')
        description = request.POST.get('description')
        decaissement = request.POST.get('decaissement', 'oui') == 'oui'

        if decaissement :
            decaissement = True
        else:
            decaissement = False

        ingredient = Ingredient.objects.get(id=id)
        ingredient.quantity = ingredient.quantity + float(quantity)
        ingredient.save()
        
        StockMovement.objects.create(
            ingredient = ingredient,
            quantity=quantity,
            unit_price=int(price),
            amount_paid=amount_paid,
            fournisseur= Fournisseur.objects.get(id=fournisseur_id),
            description=description,
            decaisement=decaissement,
            type_de_mouvement = 'Entrée'
        )

    messages.success(request, "Réapprovisionnement fait avec succès.")
    return redirect('ingredients-list')

def reaprovisionnementList(request):
    fournisseurs = Fournisseur.objects.all()  # Récupérer tous les fournisseurs
    produits = Product.objects.all()  # Récupérer tous les produits
    reaprovisionnements = Reapprovisionnement.objects.all()
    form = ReapprovisionnementForm()
    context = {
        'reaprovisionnements':reaprovisionnements,
        'form':form,
        'fournisseurs': fournisseurs,
        'produits': produits,
    }
    
    return render(request, 'pages/reaprovisionnement-list.html',context)


@csrf_exempt
def create_reapprovisionnement(request):
    try:
        fournisseurs = Fournisseur.objects.all()
        produits = Product.objects.all()

        if request.method == 'POST':
            # print(request.POST.get('decaissement', 'oui'))
            fournisseur_id = request.POST.get('fournisseur')
            decaissement = request.POST.get('decaissement', 'oui') == 'oui'
            caisse = Caisse.objects.get(user = request.user)

            reapprovisionnement = Reapprovisionnement.objects.create(
                fournisseur_id=fournisseur_id,
            )

            item_ids = request.POST.getlist('item_id[]')
            item_quantities = request.POST.getlist('item_quantity[]')
            item_prices = request.POST.getlist('item_price[]')
            total_montant = 0

            for item_id, quantity, price in zip(item_ids, item_quantities, item_prices):
                print('hellllloooooooooooooooooooo')
                product = Product.objects.get(id=item_id)
                quantite = int(quantity)
                prix_unite = float(price)
                total_montant += quantite * prix_unite

                # Créer l'item de réapprovisionnement
                newreapitems = ReapprovisionnementItem.objects.create(
                    reapprovisionnement=reapprovisionnement,
                    produit=product,
                    quantite=quantite,
                    prix=prix_unite
                )

                # Mettre à jour le stock_initial et le prix moyen du produit
                product.ajouter_stock(quantite=quantite)
                product.maj_prix_moyen(quantite, prix_unite)

            # Gestion du décaissement
            if decaissement:
                try:
                    caisse.ajouter_sortie(total_montant)
                    print('hellllloooooooooooooooooooo ca marche')
                    
                except ValueError as e:
                    reapprovisionnement.delete()
                    for item in newreapitems:
                        item.delete()
                    print('hellllloooooooooooooooooooo',e)
                    messages.error(request, "Solde de caisse insuffisant pour effectuer ce décaissement.")
                    
                    return redirect('reaprovisionnementList')

            messages.success(request, "Réapprovisionnement créé avec succès.")
            return redirect('reaprovisionnementList')

        else:
            reaprovisionnements = Reapprovisionnement.objects.all()
            return render(request, 'pages/reaprovisionnement-list.html', {
                'reaprovisionnements': reaprovisionnements,
                'fournisseurs': fournisseurs,
                'produits': produits,
            })

    except Exception as e:
        print(f"Erreur : {e}")
        messages.error(request, "Une erreur est survenue. Merci de réessayer.")
        return redirect('reaprovisionnementList')
     
def add_item_form(request):
    """
    Vue pour retourner le formulaire d'un nouvel item de réapprovisionnement.
    """
    form = ReapprovisionnementItemForm()
    return render(request, 'partials/reapprovisionnement_item_form.html', {'form': form})

def refresh_order(request):
    """Recharge les éléments de la commande pour le serveur actuel."""
    clients = Client.objects.filter(disponible=True)
    order, _ = Order.objects.get_or_create(server=request.user, status="En cours")
    return render(request, "partials/order_items.html", {"order": order, "clients": clients})

def refresh_reapovisionement(request):
    """Recharge les éléments de la commande pour le serveur actuel."""
    fournisseurs = Fournisseur.objects.filter(disponible=True)
    reapprovisionnement= get_object_or_404(Reapprovisionnement, autheur=request.user, status = 'Non Validé')
    return render(request, "partials/achat_items.html", {"reapprovisionnement": reapprovisionnement, "fournisseurs": fournisseurs})

@csrf_exempt
def creer_client(request):
    """Crée un nouveau client disponible pour les commandes en cours."""
    clients = Client.objects.filter(disponible=True)
    order, _ = Order.objects.get_or_create(server=request.user, status="En cours")

    if request.method == 'POST':
        nom, telephone, adresse = request.POST.get('nom'), request.POST.get('telephone'), request.POST.get('adresse')

        if not nom or not adresse:
            return JsonResponse({"error": "Nom et adresse sont requis."}, status=400)

        try:
            Client.objects.create(nom=nom, telephone=telephone, adresse=adresse)
            if request.headers.get("HX-Request"):
                return render(request, "partials/order_items.html", {"order": order, "clients": clients})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Méthode non autorisée."}, status=405)




def clear_order(request, order_id):
    """Supprime tous les éléments d'une commande."""
    current_order = get_object_or_404(Order, id=order_id)
    clients = Client.objects.filter(disponible=True)

    if request.method == "POST":
        OrderItem.objects.filter(order=current_order).delete()
        if request.headers.get("HX-Request"):
            return render(request, "partials/order_items.html", {"order": current_order, 'clients': clients})
        return redirect("vendor-dashboard")

    return HttpResponse(status=405)


def cancel_order(request, order_id):
    """Supprime tous les éléments d'une commande."""
    current_order = get_object_or_404(Order, id=order_id)
    clients = Client.objects.filter(disponible=True)
    order, _ = Order.objects.get_or_create(server=request.user, status="En cours")
    if request.method == "POST":
        # OrderItem.objects.filter(order=current_order).delete()
        current_order.delete = True
        current_order.status = 'Annulé' 
        current_order.save()
        if request.headers.get("HX-Request"):
            return render(request, "partials/order_items.html", {"order": order, 'clients': clients})
        return redirect("vendor-dashboard")

    return HttpResponse(status=405)

def save_order(request, order_id):
    """Enregistre et valide une commande."""
    current_order = get_object_or_404(Order, id=order_id)
    caisse, created = Caisse.objects.get_or_create(user = request.user)
    if request.method == "POST":
        try:
            montant_paye = Decimal(request.POST.get("somme_payer", 0) or 0)
            if montant_paye > 0:
                current_order.register_partial_payment(montant_paye)
                try:
                    caisse.ajouter_entree(int(montant_paye))
                except Exception as e : 
                    print(e)
                
            current_order.status = "Validé"
            current_order.save()
        
            if request.headers.get("HX-Request"):
                return render(request, "partials/order_items.html", {"order": {}})
            return redirect("vendor-dashboard")
        except (ValueError, InvalidOperation) as e:
            print(e)
            return JsonResponse({"error": "Montant invalide."}, status=400)
        except Exception as e:
            print(e)
            return JsonResponse({"error": str(e)}, status=500)

    return HttpResponse(status=405)


def save_reaprovisionement(request, id):
    """Enregistre et valide une commande."""
    current_reaprovisionement = get_object_or_404(Reapprovisionnement, id=id)
    caisse = Caisse.objects.get(user = request.user)

    if request.method == "POST":
        try:
            decaissement = request.POST.get('decaissement', 'off') == 'off'
            print(request.POST.get('decaissement'))
            print(decaissement)
            
            if not decaissement :
               try :
                    caisse.ajouter_sortie(current_reaprovisionement.prix_total)
                    current_reaprovisionement.status = "Validé"
                    current_reaprovisionement.save()
                    current_reaprovisionement.appliquer_reapprovisionnement()
               except Exception as e:
                   print(e)
                #    Notification.objects.create(user = request.user, message = f'erreur : {e}')
            else :
                current_reaprovisionement.status = "Validé"
                current_reaprovisionement.save()
                current_reaprovisionement.appliquer_reapprovisionnement()
            
            if request.headers.get("HX-Request"):
                return render(request, "partials/achat_items.html", {"reapprovisionnement":''})
            return redirect("/")
        except Exception as e:
            print(e)
            return JsonResponse({"error": str(e)}, status=500)

    return HttpResponse(status=405)


def modify_order(request, order_id):
    """Met en pause une commande."""
    current_order = get_object_or_404(Order, id=order_id,server=request.user )

    if request.method == "GET":
        current_order.status = "En cours"
        current_order.save()

        if request.headers.get("HX-Request"):
            return redirect("vendor-dashboard")

        return redirect("vendor-dashboard")

    return HttpResponse(status=405)


def paused_order(request, order_id):
    """Met en pause une commande."""
    current_order = get_object_or_404(Order, id=order_id)

    if request.method == "POST":
        current_order.status = "Mis en pause"
        current_order.save()

        if request.headers.get("HX-Request"):
            return render(request, "partials/paused_orders.html", {"paused_orders": Order.objects.filter(status="Mis en pause"), "order": current_order})

        return redirect("vendor-dashboard")

    return HttpResponse(status=405)

def unpause_order(request, order_id):
    """Réactive une commande en pause."""
    current_order = get_object_or_404(Order, id=order_id)

    if request.method == "POST":
        current_order.status = "En cours"
        current_order.save()

        if request.headers.get("HX-Request"):
            return render(request, "partials/paused_orders.html", {"paused_orders": Order.objects.filter(status="Mis en pause"), "order": current_order})

        return refresh_order(request)

    return HttpResponse(status=405)

def add_product_to_order(request):
    """Ajoute un produit à la commande en cours du serveur."""
    # Chercher une commande "En cours" sans items
    order = Order.objects.filter(server=request.user, status="En cours").first()

    # S'il n'y en a pas, on en crée une nouvelle
    if not order:
        order = Order.objects.create(server=request.user, status="En cours")

    clients = Client.objects.filter(disponible=True)

    if request.method == "POST":
        product = get_object_or_404(productSize, id=request.POST.get("product_id"))
        order_item, created = OrderItem.objects.get_or_create(order=order, size=product)

        order_item.quantity = order_item.quantity + 1 if not created else 1
        order_item.save()

       
        
        order.save()
        
        
        stickers = []
        counter = 0
        total_items_count = sum(item.quantity for item in order.items.all())  # Total d'étiquettes à générer

        for item in order.items.all():
            for _ in range(item.quantity):
                counter += 1
                stickers.append({
                    'order_id': order.daily_sequence ,
                    'product_code': item.size.product.code,
                    'size': item.size.size,
                    'counter': counter,
                    'total': total_items_count
                })

        
        if request.headers.get("HX-Request"):
            return render(request, "partials/order_items.html", {"order": order, "clients": clients ,  'stickers': stickers,})
        return redirect("vendor-dashboard", order_id=order.id)

    return HttpResponse(status=405)

def update_order_item(request, item_id):
    """Met à jour le nom et le prix personnalisé d'un élément de commande."""
    order_item = get_object_or_404(OrderItem, id=item_id)

    if request.method == "POST":
        new_name, new_price = request.POST.get("product_name"), request.POST.get("product_price")
        if new_name:
            order_item.custom_product_name = new_name
        if new_price:
            try:
                order_item.custom_product_price = Decimal(new_price)
            except InvalidOperation:
                return JsonResponse({"error": "Prix invalide."}, status=400)

        order_item.save()

        if request.headers.get("HX-Request"):
            return render(request, "partials/order_items.html", {"order": order_item.order, 'clients': Client.objects.filter(disponible=True)})
        
        return redirect("order_list")

    return HttpResponse(status=405)


def update_oreaprovisionement_item(request, item_id):
    """Met à jour le nom et le prix personnalisé d'un élément de commande."""
    reaprovisionement_item = get_object_or_404(ReapprovisionnementItem, id=item_id)

    if request.method == "POST":
        prix_achat, prix_de_vente = request.POST.get("prix_achat"), request.POST.get("prix_de_vente")
        if prix_achat:
            reaprovisionement_item.prix_achat = prix_achat
        if prix_de_vente:
            try:
                reaprovisionement_item.prix_de_vente = Decimal(prix_de_vente)
            except InvalidOperation:
                return JsonResponse({"error": "Prix invalide."}, status=400)

        reaprovisionement_item.save()

        if request.headers.get("HX-Request"):
            return render(request, "partials/achat_items.html", {"reapprovisionnement": reaprovisionement_item.reapprovisionnement, 'fournisseurs': Fournisseur.objects.filter(disponible=True)})
        
        return redirect("/")

    return HttpResponse(status=405)


def choose_customer(request, id):
    """Assigne un client à une commande et met à jour les dettes uniquement en cas de changement de client."""
    current_order = get_object_or_404(Order, id=id)

    if request.method == "POST":
        client_id = request.POST.get("client_id")
        new_client = Client.objects.get(id=client_id)

        # Vérifie si le client a changé avant de mettre à jour les dettes
        if current_order.client != new_client:
            # Réduit la dette de l'ancien client si un client était déjà assigné
            if current_order.client:
                old_client = current_order.client
                old_client.save(update_fields=["dette"])

            # Assigne le nouveau client à la commande
            current_order.client = new_client
            current_order.status = "En cours"
            current_order.save(update_fields=["client", "status"])

            # Incrémente la dette du nouveau client
            new_client.save(update_fields=["dette"])

        # Réponse partielle si c'est une requête HTMX, sinon redirection
        if request.headers.get("HX-Request"):
            return render(request, "partials/order_items.html", {"order": current_order, "clients": Client.objects.filter(disponible=True)})
        
        return redirect("order_list")

    return HttpResponse(status=405)

def choose_fournissuer(request, id):
    reapprovisionnement = get_object_or_404(Reapprovisionnement, id=id)

    if request.method == "POST":
        founrniseur_id = request.POST.get("fourniseur_id")
        print(request.POST.get("fourniseur_id"))
        reapprovisionnement.fournisseur = Fournisseur.objects.get(id=founrniseur_id)
        reapprovisionnement.save()

        if request.headers.get("HX-Request"):
            return render(request, "partials/achat_items.html", {"reapprovisionnement": reapprovisionnement, "fournisseurs": Fournisseur.objects.filter(disponible=True)})
        return redirect("/")

    return HttpResponse(status=405)

def update_payment(request, order_id):
    """Met à jour le paiement d'une commande."""
    current_order = get_object_or_404(Order, id=order_id)
    clients = Client.objects.filter(disponible=True)

    if request.method == "POST":
        try:
            montant_paye = Decimal(request.POST.get("montant_remise", 0) or 0)
            if montant_paye > 0:
                current_order.register_partial_payment(montant_paye)
                current_order.save()

            if request.headers.get("HX-Request"):
                return render(request, "partials/order_items.html", {"order": current_order, "clients": clients})
            return redirect("vendor-dashboard")
        except (ValueError, InvalidOperation)   as e:
            print(e)
            return JsonResponse({"error": "Montant invalide."}, status=400)
        except Exception as e:
            print('error:',e)
            return JsonResponse({"error": str(e)}, status=500)

    return HttpResponse("Méthode POST attendue.", status=405)

def update_reaprovisionement_payment(request, id):
    """Met à jour le paiement d'une commande."""
    current_reapprovisionnement = get_object_or_404(Reapprovisionnement, id=id)
    fournisseurs = Fournisseur.objects.filter(disponible=True)

    if request.method == "POST":
        try:
            montant_paye = Decimal(request.POST.get("somme_payer", 0) or 0)
            print(Decimal(request.POST.get("somme_payer", 0) or 0))
            if montant_paye > 0:
                current_reapprovisionnement.register_partial_payment(montant_paye)
                current_reapprovisionnement.save()

           
            return render(request, "partials/achat_items.html", {"reapprovisionnement": current_reapprovisionnement, "fournisseurs": fournisseurs})
            
        except (ValueError, InvalidOperation) as e:
            print('error:',e)
            return JsonResponse({"error": "Montant invalide."}, status=400)
        except Exception as e:
            print('error:',e)
            return JsonResponse({"error": str(e)}, status=500)

    return HttpResponse("Méthode POST attendue.", status=405)
def increment_order_item(request, item_id):
    """Incrémente la quantité d'un élément dans la commande et met à jour la dette du client."""
    order_item = get_object_or_404(OrderItem, id=item_id)
    client = order_item.order.client

    if request.method == "POST":
        # Calcul de l'augmentation de la dette en fonction du prix de l'article
        previous_quantity = order_item.quantity
        order_item.quantity += 1
        order_item.save(update_fields=["quantity"])

        # Calcul du coût supplémentaire et mise à jour de la dette
        item_price = order_item.size.price.amount  # Supposons que chaque `OrderItem` a un attribut `price`
        additional_cost = item_price * (order_item.quantity - previous_quantity)
        client.dette += additional_cost
        client.save(update_fields=["dette"])

        # Réponse partielle si c'est une requête HTMX, sinon redirection
        if request.headers.get("HX-Request"):
            return render(request, "partials/order_items.html", {"order": order_item.order, "clients": Client.objects.filter(disponible=True)})

        return redirect("order_list")

    return HttpResponse(status=405)

def increment_reaprovisionement_item(request, item_id):
    """Incrémente la quantité d'un élément dans la commande."""
    reaprovisionement_item = get_object_or_404(ReapprovisionnementItem, id=item_id)

    if request.method == "POST":
        reaprovisionement_item.quantite += 1
        reaprovisionement_item.save()

        if request.headers.get("HX-Request"):
            return render(request, "partials/achat_items.html", {"reapprovisionnement": reaprovisionement_item.reapprovisionnement, "fournisseurs": Fournisseur.objects.filter(disponible=True)})
        return redirect("/")

    return HttpResponse(status=405)

def decrement_order_item(request, item_id):
    """Décrémente la quantité d'un élément dans la commande (minimum 1) et met à jour la dette du client."""
    order_item = get_object_or_404(OrderItem, id=item_id)
    client = order_item.order.client

    if request.method == "POST" and order_item.quantity > 1:
        # Calcul de la réduction de la dette en fonction du prix de l'article
        previous_quantity = order_item.quantity
        order_item.quantity -= 1
        order_item.save(update_fields=["quantity"])

        # Calcul du coût réduit et mise à jour de la dette
        item_price = order_item.size.price.amount  # Assumant que chaque `OrderItem` a un attribut `price`
        reduction_cost = item_price * (previous_quantity - order_item.quantity)
        client.dette -= reduction_cost
        client.save(update_fields=["dette"])

        # Réponse partielle si c'est une requête HTMX, sinon redirection
        if request.headers.get("HX-Request"):
            return render(request, "partials/order_items.html", {"order": order_item.order, "clients": Client.objects.filter(disponible=True)})

        return redirect("order_list")

    return HttpResponse(status=405)

def decrement_reaprovisionement_item(request, item_id):
    """Décrémente la quantité d'un élément dans la commande (minimum 1)."""
    reaprovisionement_item = get_object_or_404(ReapprovisionnementItem, id=item_id)

    if request.method == "POST" and reaprovisionement_item.quantite > 1:
        reaprovisionement_item.quantite -= 1
        reaprovisionement_item.save()

        if request.headers.get("HX-Request"):
            return render(request, "partials/achat_items.html", {"reapprovisionnement": reaprovisionement_item.reapprovisionnement, "fournisseurs": Fournisseur.objects.filter(disponible=True)})
        return redirect("/")

    return HttpResponse(status=405)


def delete_order_item(request, item_id):
    """Supprime un élément de la commande et met à jour la dette du client."""
    clients = Client.objects.filter(disponible=True)

    if request.method == "POST":
        order_item = get_object_or_404(OrderItem, id=item_id)
        order = order_item.order  # Obtenir l'ordre directement depuis l'élément

        # Mettre à jour la dette du client avant la suppression
        client = order.client
        item_price = order_item.size.price.amount  # Récupérer le prix de l'article
        total_item_cost = item_price * order_item.quantity  # Coût total de l'élément à supprimer
        client.dette -= total_item_cost  # Soustraire le coût de la dette
        client.save(update_fields=["dette"])  # Sauvegarder les modifications

        # Supprimer l'élément de commande
        order_item.delete()

        # Recalculer le montant restant de la commande
        order.save()  # Sauvegarder les modifications

        # Réponse partielle avec HTMX
        if request.headers.get("HX-Request"):
            return render(
                request, "partials/order_items.html", {"order": order, "clients": clients}
            )

        return redirect("order_list")

    return HttpResponse(status=405)


def delete_reaprovisionement_item(request, item_id):
    
    """Supprime un élément de la commande"""
    if request.method == "POST":
        reaprovisionement_item = get_object_or_404(ReapprovisionnementItem, id=item_id)
        reaprovisionement_item.delete()
        # Réponse partielle avec HTMX
        if request.headers.get("HX-Request"):
            return render(request, "partials/achat_items.html", {"reapprovisionnement": reaprovisionement_item.reapprovisionnement, "fournisseurs": Fournisseur.objects.filter(disponible=True)})
        return redirect("/")

    return HttpResponse(status=405)

def delete_paused_order(request, order_id):
    paused_orders = Order.objects.filter(status="Mis en pause")
        # Supprime la commande
    del_it = Order.objects.filter(id=order_id, status="Mis en pause")
    del_it.delete()
    # Si la requête vient d'HTMX
    if request.headers.get("HX-Request"):
        # Réponse partielle pour mettre à jour la liste des commandes en pause
        return render(
            request, "partials/paused_orders.html", {"paused_orders": paused_orders}
        )

        # Redirige vers la page principale si ce n'est pas une requête HTMX
        return redirect("vendor-dashboard")

    return HttpResponse(status=405)

def add_product_to_reapo(request):
    """Ajoute un produit à la commande en cours du serveur."""
    reapprovisionnement, _= Reapprovisionnement.objects.get_or_create(autheur=request.user, status ='Non Validé')
    fournisseur = Fournisseur.objects.filter(disponible=True)

    if request.method == "POST":
        product = get_object_or_404(Product, id=request.POST.get("product_id"))
        prix_achat = product.prix_achat
        prix_de_vente = product.prix_de_vente
        # qty=request.POST.get("qty")
        reapprovisionnement_item, created = ReapprovisionnementItem.objects.get_or_create(produit=product,reapprovisionnement = reapprovisionnement, prix_achat = prix_achat, prix_de_vente = prix_de_vente)

        reapprovisionnement_item.quantite = reapprovisionnement_item.quantite + 1 if not created else 1
        reapprovisionnement_item.save()
        reapprovisionnement.montant_restant = reapprovisionnement.get_total()
        # reapprovisionnement.montant_restant = reapprovisionnement.get_total()
        reapprovisionnement.fournisseur = Fournisseur.objects.first()
        reapprovisionnement.save()

        if request.headers.get("HX-Request"):
            return render(request, "partials/achat_items.html", {"reapprovisionnement": reapprovisionnement, "fournisseurs": fournisseur})
        return redirect("achat", reapprovisionnement_id=reapprovisionnement.id)

    return HttpResponse(status=405)


def fiche_Stock(request):
    fiche_stock = FicheStock.objects.annotate(
        nombre_entrees=Count('mouvements', filter=Q(mouvements__type_mouvement="ENTRÉE")),
        nombre_sorties=Count('mouvements', filter=Q(mouvements__type_mouvement="SORTIE")),
        nombre_autre=Count('mouvements', filter=Q(mouvements__type_mouvement="AUTRE")),
        total_entrees=Sum('mouvements__quantite', filter=Q(mouvements__type_mouvement="ENTRÉE")),
        total_sorties=Sum('mouvements__quantite', filter=Q(mouvements__type_mouvement="SORTIE")),
        date_dernier_mouvement=Max('mouvements__date_mouvement')  # Date du dernier mouvement, renommée
    )
    context= {
        'fiche_stock':fiche_stock,
    }
    return render(request, 'pages/fiche_de_stock.html', context)



@csrf_exempt
def creer_fournisseur(request):
    """Crée un nouveau client disponible pour les commandes en cours."""
    fournisseurs = Fournisseur.objects.filter(disponible=True)
    reapprovisionnement, _= Reapprovisionnement.objects.get_or_create(autheur=request.user, status ='Non Validé')

    if request.method == 'POST':
        nom, telephone, adresse = request.POST.get('nom'), request.POST.get('telephone'), request.POST.get('adresse')

        if not nom or not adresse:
            return JsonResponse({"error": "Nom et adresse sont requis."}, status=400)

        try:
            Fournisseur.objects.create(nom=nom, telephone=telephone, adresse=adresse)
            if request.headers.get("HX-Request"):
                return render(request, "partials/achat_items.html", {"reapprovisionnement": reapprovisionnement, "fournisseurs": fournisseurs})
        except Exception as e:
            print(e)
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Méthode non autorisée."}, status=405)



def cash_expense(request):
    depenses = Depense.objects.filter(delete = False)
    add_form = DepenseAddForm()  # Formulaire d'ajout
    update_form = DepenseUpdateForm()  # Formulaire de modification (vide par défaut)
    delete_form = DepenseDeleteForm()  # Formulaire de suppression

    context = {
        'depenses': depenses,
        'add_form': add_form,
        'update_form': update_form,
        'delete_form': delete_form,
    }
    return render(request, 'pages/depense.html' ,context )


# Vue principale
def cash_expense(request):
    depenses = Depense.objects.filter(delete=False)
    date_debut = request.GET.get("date_debut")
    date_fin = request.GET.get("date_fin")

    if date_debut and date_fin:
        depenses = depenses.filter(date__range=[date_debut, date_fin])
    
    update_forms = {dep.id: DepenseUpdateForm(instance=dep) for dep in depenses}
    
    context = {
        'depenses': depenses,
        'add_form': DepenseAddForm(),
        'delete_form': DepenseDeleteForm(),
        'update_forms': update_forms
    }
    return render(request, 'pages/depense.html', context)


# Ajouter une dépense
def add_expense(request):
    if request.method == 'POST':
        form = DepenseAddForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Dépense ajoutée avec succès !")
        else:
            messages.error(request, "Erreur lors de l'ajout de la dépense.")
    return redirect('depense')

# Mettre à jour une dépense
def update_expense(request, id):
    depense = get_object_or_404(Depense, id=id)
    if request.method == 'POST':
        form = DepenseUpdateForm(request.POST, request.FILES, instance=depense)
        if form.is_valid():
            form.save()
            messages.success(request, "Dépense mise à jour !")
        else:
            messages.error(request, "Erreur lors de la mise à jour.")
    return redirect('depense')

# Suppression logique avec HTMX
def delete_expense(request, id):
    depense = get_object_or_404(Depense, id=id)
    depense.delete = True
    depense.save()
    return HttpResponse("")
