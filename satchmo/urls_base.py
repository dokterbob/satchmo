"""Base urls used by Satchmo.

Split out from urls.py to allow much easier overriding and integration with larger apps.
"""
from django.conf import settings
from django.conf.urls.defaults import *
from satchmo.shop import get_satchmo_setting
from satchmo.shop.views.sitemaps import sitemaps

shop_base = get_satchmo_setting('SHOP_BASE')
if shop_base == '':
    shopregex = '^'
else:
    shopregex = '^' + shop_base[1:] + '/'

urlpatterns = patterns('',
    (r'^admin/print/(?P<doc>[-\w]+)/(?P<id>\d+)', 
        'satchmo.shipping.views.displayDoc', {}, 
        'satchmo_print_shipping'),
    (r'^admin/product/configurableproduct/(?P<id>\d+)/getoptions/', 
        'satchmo.product.views.get_configurable_product_options', {}, 
        'satchmo_admin_configurableproduct'),
    (r'^admin/doc/', include('django.contrib.admindocs.urls')),
    (r'^accounts/', include('satchmo.accounts.urls')),
    (shopregex, include('satchmo.shop.urls')),
    (r'sitemap\.xml$', 'django.contrib.sitemaps.views.sitemap', 
        {'sitemaps': sitemaps}, 
        'satchmo_sitemap_xml'),
    (r'settings/', include('satchmo.configuration.urls')),
    (r'cache/', include('satchmo.caching.urls')),
)

