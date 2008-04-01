from django.conf.urls.defaults import *

urlpatterns = patterns('satchmo.feeds.views',
    (r'atom/$', 'product_feed', {'template' : "feeds/googlebase_atom.xml"}, 'satchmo_atom_feed'),
    (r'products.csv$', 'admin_product_feed', {'template' : "feeds/product_feed.csv"}, 'satchmo_product_feed'),
)

