from django.conf import settings
from django.conf.urls.defaults import *
from satchmo.configuration import config_value
from satchmo.product.models import Product
from satchmo.product.views import display_featured
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
    (r'^category/(?P<parent_slugs>[-\w]+/)*(?P<slug>[-\w]+)/$', 'category.display', {}, 'satchmo_category'),
    (r'^checkout/', include('satchmo.payment.urls')),
    (r'^contact/$', 'contact.form', {}, 'satchmo_contact'),
    (r'^history/$', 'orders.order_history', {}, 'satchmo_order_history'),
    (r'^product/', include('satchmo.product.urls')),
    (r'^tracking/(?P<order_id>\d+)/$', 'orders.order_tracking', {}, 'satchmo_order_tracking'),

    # Override comments with our redirecting view. You can remove the next two
    # URLs if you aren't using ratings.
    (r'^comments/post/$', 'comments.post_rating', {'maxcomments': 1 }, 'satchmo_rating_post'),
    (r'^comments/', include('django.contrib.comments.urls.comments')),

    # Used to set the default language.
    (r'^i18n/', include('django.conf.urls.i18n')),

    # Used for downloadable products.
    (r'^download/process/(?P<download_key>\w+)/$', 'download.process', {}, 'satchmo_download_process'),
    (r'^download/send/(?P<download_key>\w+)/$', 'download.send_file', {}, 'satchmo_download_send'),
)

urlpatterns += patterns('satchmo.product.views',
    (r'^search/$', 'do_search', {}, 'satchmo_search'),
)

if app_enabled('wishlist'):
    urlpatterns += patterns('',
        ('wishlist/', include('satchmo.wishlist.urls')),
    )

urlpatterns += patterns('django.views.generic',
    (r'^contact/thankyou/$','simple.direct_to_template',{'template':'thanks.html'}),
)

# Make sure thumbnails and images are served up properly when using the dev server.
if settings.LOCAL_DEV:
    urlpatterns += patterns('',
        (r'^site_media/(.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
    )
