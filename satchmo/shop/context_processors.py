"""
This code is heavily based on samples found here -
http://www.b-list.org/weblog/2006/06/14/django-tips-template-context-processors

It is used to add some common variables to all the templates
"""
from django.conf import settings as site_settings
from satchmo.product.models import Category
from satchmo.shop.models import Config, NullConfig, Cart, NullCart
from satchmo.shop.utils import request_is_secure
import logging

log = logging.getLogger('shop_context')

def settings(request):
    shop_config = Config.get_shop_config()
    cart = Cart.objects.from_request(request)

    all_categories = Category.objects.all()

    # handle secure requests
    media_url = site_settings.MEDIA_URL
    secure = request_is_secure(request)
    if secure:
        try:
            media_url = site_settings.MEDIA_SECURE_URL
        except AttributeError:
            media_url = media_url.replace('http://','https://')

    return {
        'shop_base': site_settings.SHOP_BASE,
        'shop' : shop_config,
        'shop_name': shop_config.store_name,
        'media_url': media_url,
        'cart_count': cart.numItems,
        'cart': cart,
        'categories': all_categories,
        'is_secure' : secure,
        'request' : request,
    }
