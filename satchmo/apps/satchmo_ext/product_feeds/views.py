import datetime
from django.contrib.auth.decorators import user_passes_test
from django.core import urlresolvers
from django.http import Http404
from django.shortcuts import get_object_or_404, render_to_response
from payment.config import credit_choices
from product.models import Product, Category
from satchmo_store.shop.models import Config
from django.utils.translation import ugettext_lazy as _

@user_passes_test(lambda u: u.is_authenticated() and u.is_staff, login_url='/accounts/login/')
def admin_product_feed(request, category=None, template="product_feeds/product_feed.csv", mimetype="text/csv"):
    """Admin authenticated feed - same as product feed but for different types of feeds.
    """
    return product_feed(request, category=category, template=template, mimetype=mimetype)

def product_feed(request, category=None, template="product_feeds/googlebase_atom.xml", mimetype="application/atom+xml"):
    """Build a feed of all active products.
    """

    shop_config = Config.objects.get_current()
    if category:
        try:
            cat = Category.objects.active().get(slug=category)
            products = cat.active_products()
        except Category.DoesNotExist:
            raise Http404, _("Bad Category: %s" % category)
    else:
        cat = None
        products = Product.objects.active_by_site()
        
    products = filter(lambda product:"ConfigurableProduct" not in product.get_subtypes(), products)
    
    params = {}
    view = 'satchmo_atom_feed'
    if category:
        params['category'] = category
        view = 'satchmo_atom_category_feed'
    
    url = shop_config.base_url + urlresolvers.reverse(view, None, params)
    
    payment_choices = [c[1] for c in credit_choices(None, True)]
    
    return render_to_response(template, {
        'products' : products,
        'category' : cat,
        'url' : url,
        'shop' : shop_config,
        'payments' : payment_choices,
        'date' : datetime.datetime.now(),
        },
        mimetype=mimetype)
