import datetime
from django.core import urlresolvers
from django.http import Http404
from django.shortcuts import get_object_or_404, render_to_response
from satchmo.payment.config import credit_choices
from satchmo.product.models import Product, Category
from satchmo.shop.models import Config

def product_feed(request, category=None, template="feeds/googlebase_atom.xml"):
    """Build a feed of all active products.
    """

    shop_config = Config.get_shop_config()
    if category:
        try:
            cat = Category.objects.get(slug=category)
            products = Category.active_products()
        except Category.DoesNotExist:
            raise Http404, _("Bad Category: %s" % category)
    else:
        cat = None
        products = Product.objects.filter(active=True)
        
    url = shop_config.base_url + urlresolvers.reverse('satchmo_atom_feed', None, { 
        'category' : category, 
        'template' : template 
    })
    
    payment_choices = [c[1] for c in credit_choices(None, True)]
    
    return render_to_response(template, {
        'products' : products,
        'category' : cat,
        'url' : url,
        'shop' : shop_config,
        'payments' : payment_choices,
        'date' : datetime.datetime.now(),
        })
