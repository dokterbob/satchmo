from django.conf.urls.defaults import *

urlpatterns = patterns('satchmo.feeds.views',
    (r'atom/$', 'product_feed', {}, 'satchmo_atom_feed'),
    (r'atom/(?P<category>\w+)/$', 'product_feed', {}, 'satchmo_atom_category_feed'),
    (r'products.csv$', 'admin_product_feed', {'template' : "feeds/product_feed.csv"}, 'satchmo_product_feed'),
)

