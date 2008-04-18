from django.conf.urls.defaults import *

import logging

urlpatterns = patterns('satchmo.wishlist.views',
     (r'^$', 'wishlist_view', {}, 'satchmo_wishlist_view'),
     (r'^add/$', 'wishlist_add', {}, 'satchmo_wishlist_add'),
     (r'^add/ajax/$', 'wishlist_add_ajax', {}, 'satchmo_wishlist_add_ajax'),
     (r'^remove/$', 'wishlist_remove', {}, 'satchmo_wishlist_remove'),
     (r'^remove/ajax$', 'wishlist_remove_ajax', {}, 'satchmo_wishlist_remove_ajax'),
     (r'^add_cart/$', 'wishlist_move_to_cart', {}, 'satchmo_wishlist_move_to_cart'),
)