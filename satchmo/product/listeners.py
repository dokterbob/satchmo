from django.contrib.sites.models import Site
from django.db.models import Q
from satchmo.product.models import Product, Category
import logging
log = logging.getLogger('search listener')

def default_product_search_listener(sender, request=None, category=None, keywords=[], results={}, **kwargs):
    """Performs the base satchmo search.  This is easily overridden by unregistering the listener and creating your own.
    However, it usually won't have to be overridden, since it just adds data to the results dict.  If you are simply
    adding more results, then leave this listener registered and add more objects in your search listener.
    """
    site = Site.objects.get_current()
    products = Product.objects.all()
    productkwargs = {
        'productvariation__parent__isnull' : True,
        'active' : True,
        'site' : site
    }

    if category:
        categories = Category.objects.filter(slug=category)
        if categories:
            categories = categories[0].get_active_children(include_self=True)
        
        productkwargs['category__in'] = categories
    else:
        categories = Category.objects.all()

    for keyword in keywords:
        if not category:
            categories = categories.filter(
                Q(name__icontains=keyword) |
                Q(meta__icontains=keyword) |
                Q(description__icontains=keyword),
                site=site,)
                
        products = products.filter(
            Q(name__icontains=keyword)
            | Q(short_description__icontains=keyword)
            | Q(description__icontains=keyword)
            | Q(meta__icontains=keyword)
            | Q(sku__iexact=keyword),
            **productkwargs)
                        
    clist = list(categories)
    #plist = [p for p in products if not p.has_variants]
    plist = list(products)
    
    results.update({
        'categories': clist, 
        'products': plist
        })
