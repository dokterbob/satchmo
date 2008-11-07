from django.conf import settings
from django.conf.urls.defaults import *
from satchmo.configuration import config_value
from satchmo.product.urls import urlpatterns as productpatterns
from satchmo.shop import get_satchmo_setting
from satchmo.utils import app_enabled

urlpatterns = get_satchmo_setting('SHOP_URLS')

urlpatterns += patterns('satchmo.shop.views',
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
    (r'^checkout/', include('satchmo.payment.urls')),
    (r'^contact/$', 'contact.form', {}, 'satchmo_contact'),
    (r'^history/$', 'orders.order_history', {}, 'satchmo_order_history'),
    (r'^tracking/(?P<order_id>\d+)/$', 'orders.order_tracking', {}, 'satchmo_order_tracking'),
    (r'^search/$', 'search.search_view', {}, 'satchmo_search'),

    # Override comments with our redirecting view. You can remove the next two
    # URLs if you aren't using ratings.
    #(r'^comments/post/$', 'comments.post_rating', {'maxcomments': 1 }, 'satchmo_rating_post'),
    (r'^comments/', include('django.contrib.comments.urls')),
    
    # Used for downloadable products.
    (r'^download/process/(?P<download_key>\w+)/$', 'download.process', {}, 'satchmo_download_process'),
    (r'^download/send/(?P<download_key>\w+)/$', 'download.send_file', {}, 'satchmo_download_send'),
)

# here we add product patterns directly into the root url
urlpatterns += productpatterns

if app_enabled('l10n'):
    urlpatterns += patterns('',
        # Used to set the default language.
        (r'^i18n/', include('satchmo.l10n.urls'))
    )

if app_enabled('wishlist'):
    urlpatterns += patterns('',
        ('wishlist/', include('satchmo.wishlist.urls')),
    )

urlpatterns += patterns('django.views.generic',
    (r'^contact/thankyou/$','simple.direct_to_template',{'template':'thanks.html'},'satchmo_contact_thanks'),
)

# Make sure thumbnails and images are served up properly when using the dev server.
if getattr(settings, 'LOCAL_DEV', False):
    urlpatterns += patterns('',
        (r'^site_media/(.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
    )
