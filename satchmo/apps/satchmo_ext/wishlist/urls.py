"""
Urls for wishlists, note that this does not have to get added manually to the urls, it will be added automatically by satchmo core if this app is installed.
"""
from django.conf.urls.defaults import *
from livesettings import config_value
import logging

log = logging.getLogger('wishlist.urls')

urlpatterns = patterns('satchmo_ext.wishlist.views',
     (r'^$', 'wishlist_view', {}, 'satchmo_wishlist_view'),
     (r'^add/$', 'wishlist_add', {}, 'satchmo_wishlist_add'),
     (r'^add/ajax/$', 'wishlist_add_ajax', {}, 'satchmo_wishlist_add_ajax'),
     (r'^remove/$', 'wishlist_remove', {}, 'satchmo_wishlist_remove'),
     (r'^remove/ajax$', 'wishlist_remove_ajax', {}, 'satchmo_wishlist_remove_ajax'),
     (r'^add_cart/$', 'wishlist_move_to_cart', {}, 'satchmo_wishlist_move_to_cart'),
)

wishbase = r'^' + config_value('SHOP','WISHLIST_SLUG') + '/'    
wishpatterns = patterns('',
    (wishbase, include('satchmo_ext.wishlist.urls'))
)

def add_wishlist_urls(sender, patterns=(), **kwargs):
    log.debug('adding wishlist urls at %s', wishbase)
    patterns += wishpatterns
