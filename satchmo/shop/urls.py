from django.conf.urls.defaults import *
from django.conf import settings
from satchmo.product.models import Product

#The following views are custom to Satchmo

urlpatterns = getattr(settings, 'SHOP_URLS', [])

urlpatterns += patterns('satchmo.shop.views',
    (r'^category/(?P<slug>[-\w]+)/$', 'category.root'),
    (r'^category/(?P<slug_parent>[-\w]+)/(?P<slug>[-\w]+)/$', 'category.children'),
    (r'^category/([-\w]+/)+(?P<slug_parent>[-\w]+)/(?P<slug>[-\w]+)/$', 'category.children'),
    (r'^cart/add/$', 'cart.add', {}, 'satchmo_cart_add'),
    (r'^cart/add/ajax/$', 'cart.add_ajax', {}, 'satchmo_cart_add_ajax'),
    (r'^cart/remove/$', 'cart.remove', {}, 'satchmo_cart_remove'),
    (r'^cart/remove/ajax$', 'cart.remove_ajax', {}, 'satchmo_cart_remove_ajax'),
    (r'^cart/qty/$', 'cart.set_quantity', {}, 'satchmo_cart_set_qty'),
    (r'^cart/qty/ajax/$', 'cart.set_quantity_ajax', {}, 'satchmo_cart_set_qty_ajax'),
    (r'^cart/$', 'cart.display', {}, 'satchmo_cart'),
    (r'^contact/$', 'contact.form', {}, 'satchmo_contact'),
    # override comments with our redirecting one.  OK to remove the next two URLs if you aren't using ratings
    (r'^comments/post/$', 'comments.post_rating', { 'maxcomments' : 1 }, 'satchmo_rating_post'), 
    (r'^comments/', include('django.contrib.comments.urls.comments')),
    (r'^product/', include('satchmo.product.urls')),
    # The following url is used for downloadable products
    (r'^download/process/(?P<download_key>\w+)/$', 'download.process', {}, 'satchmo_download_process'),
    (r'^download/send/(?P<download_key>\w+)/$', 'download.send_file', {}, 'satchmo_download_send'),
    #Used to set the default language
    (r'^i18n/', include('django.conf.urls.i18n')),
)
#Note with the last category url - this allows category depth to be as deep as we want but the downside
#is that we ignore all but the child and parent category.  In practice this should be ok

urlpatterns += patterns('satchmo.product.views',
    (r'^search/$', 'do_search', {}, 'satchmo_search'),
)

#Dictionaries for generic views used in Satchmo

index_dict = {
    'queryset': Product.objects.filter(active="1").filter(featured="1"),
    'template_object_name': 'all_products',
    'template_name': 'base_index.html',
    'allow_empty': True,
    'paginate_by': 10,
}

urlpatterns += patterns('django.views.generic',
    (r'^$','list_detail.object_list',index_dict),
    (r'^contact/thankyou/$','simple.direct_to_template',{'template':'thanks.html'}),
)

# add checkout urls
urlpatterns += patterns('',
    (r'^checkout/', include('satchmo.payment.urls')),
)

#Make sure thumbnails and images are served up properly when using the dev server
if settings.LOCAL_DEV:
    urlpatterns += patterns('',
        (r'^site_media/(.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
    )
