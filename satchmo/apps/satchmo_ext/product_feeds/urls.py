"""
Urls for product feeds, note that this does not have to get added manually to the urls, it will be added automatically by satchmo core if this app is installed.
"""
from django.conf.urls.defaults import *
import logging
log = logging.getLogger('product_feeds.urls')

urlpatterns = patterns('satchmo_ext.product_feeds.views',
    (r'atom/$', 'product_feed', {}, 'satchmo_atom_feed'),
    (r'atom/(?P<category>\w+)/$', 'product_feed', {}, 'satchmo_atom_category_feed'),
    (r'products.csv$', 'admin_product_feed', {'template' : "product_feeds/product_feed.csv"}, 'satchmo_product_feed'),
)

feedpatterns = patterns('',
    (r'^feed/', include('satchmo_ext.product_feeds.urls'))
)

def add_feed_urls(sender, patterns=(), **kwargs):
    log.debug("Adding product_feed urls")
    patterns += feedpatterns
