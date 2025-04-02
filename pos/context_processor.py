from pos.models import Order


def default(request):
   try :
    order, _ = Order.objects.get_or_create(server=request.user, status="En cours")
    # Initialiser une liste pour stocker chaque étiquette
    stickers = []
    counter = 0
    total_items_count = sum(item.quantity for item in order.items.all())  # Total d'étiquettes à générer

    for item in order.items.all():
        for _ in range(item.quantity):
            counter += 1
            stickers.append({
                'order_id': order.id,
                'product_code': item.size.product.code,
                'size': item.size.size,
                'counter': counter,
                'total': total_items_count
            })

    return {
        'order': order,
        'stickers': stickers,
    }
   except :
         return {}