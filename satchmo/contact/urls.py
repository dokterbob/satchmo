"""
URLConf for Satchmo Contacts.
"""

from django.conf.urls.defaults import *

urlpatterns = patterns('satchmo.contact.views',
    (r'^$', 'view', {}, 'satchmo_account_info'),
    (r'^history/$', 'order_history', {}, 'satchmo_order_history'),
    (r'^tracking/(?P<order_id>\d+)/$', 'order_tracking', {}, 'satchmo_order_tracking'),
    (r'^update/$', 'update', {}, 'satchmo_profile_update'), 
)
