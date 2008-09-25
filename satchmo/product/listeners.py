from django.db.models import Q
from satchmo.product.models import Product, Category

def default_product_search_listener(sender, request=None, category=None, keywords=[], results={}, **kwargs):
    """Performs the base satchmo search.  This is easily overridden by unregistering the listener and creating your own.
    However, it usually won't have to be overridden, since it just adds data to the results dict.  If you are simply
    adding more results, then leave this listener registered and add more objects in your search listener.
    """
    categories = Category.objects.by_site()
    products = Product.objects.active()
    if category:
        categories = categories.filter(
            Q(name__icontains=category) |
            Q(meta__icontains=category) |
            Q(description__icontains=category))

    for keyword in keywords:
        if not category:
            categories = categories.filter(
                Q(name__icontains=keyword) |
                Q(meta__icontains=keyword) |
                Q(description__icontains=keyword))
        products = products.filter(Q(name__icontains=keyword)
            | Q(short_description__icontains=keyword)
            | Q(description__icontains=keyword)
            | Q(meta__icontains=keyword)
            | Q(sku__iexact=keyword))
    clist = list(categories)
    plist = [p for p in products if not p.has_variants]
    results.update({
        'categories': clist, 
        'products': plist
        })
