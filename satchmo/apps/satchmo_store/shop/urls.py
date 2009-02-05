from django.conf import settings
from django.conf.urls.defaults import *
from product.urls import urlpatterns as productpatterns
from satchmo_store import shop
from satchmo_store.shop.views.sitemaps import sitemaps
from satchmo_utils.signals import collect_urls

urlpatterns = shop.get_satchmo_setting('SHOP_URLS')

urlpatterns += patterns('satchmo_store.shop.views',
    (r'^$','home.home', {}, 'satchmo_shop_home'),
    (r'^add/$', 'smart.smart_add', {}, 'satchmo_smart_add'),
    (r'^cart/$', 'cart.display', {}, 'satchmo_cart'),
    (r'^cart/accept/$', 'cart.agree_terms', {}, 'satchmo_cart_accept_terms'),
    (r'^cart/add/$', 'cart.add', {}, 'satchmo_cart_add'),
    (r'^cart/add/ajax/$', 'cart.add_ajax', {}, 'satchmo_cart_add_ajax'),
    (r'^cart/qty/$', 'cart.set_quantity', {}, 'satchmo_cart_set_qty'),
    (r'^cart/qty/ajax/$', 'cart.set_quantity_ajax', {}, 'satchmo_cart_set_qty_ajax'),
    (r'^cart/remove/$', 'cart.remove', {}, 'satchmo_cart_remove'),
    (r'^cart/remove/ajax$', 'cart.remove_ajax', {}, 'satchmo_cart_remove_ajax'),
    (r'^checkout/', include('payment.urls')),
    (r'^contact/$', 'contact.form', {}, 'satchmo_contact'),
    (r'^history/$', 'orders.order_history', {}, 'satchmo_order_history'),
    (r'^quickorder/$', 'cart.add_multiple', {}, 'satchmo_quick_order'),
    (r'^tracking/(?P<order_id>\d+)/$', 'orders.order_tracking', {}, 'satchmo_order_tracking'),
    (r'^search/$', 'search.search_view', {}, 'satchmo_search'),
    
    # Used for downloadable products.
    (r'^download/process/(?P<download_key>\w+)/$', 'download.process', {}, 'satchmo_download_process'),
    (r'^download/send/(?P<download_key>\w+)/$', 'download.send_file', {}, 'satchmo_download_send'),
)

# here we add product patterns directly into the root url
urlpatterns += productpatterns

urlpatterns += patterns('',
    (r'^contact/thankyou/$','django.views.generic.simple.direct_to_template',
        {'template':'shop/contact_thanks.html'},'satchmo_contact_thanks'),
    (r'^sitemap\.xml$', 'django.contrib.sitemaps.views.sitemap', 
        {'sitemaps': sitemaps}, 
        'satchmo_sitemap_xml'),
    
)

# here we are sending a signal to add patterns to the base of the shop.
collect_urls.send(sender=shop, patterns=urlpatterns)
