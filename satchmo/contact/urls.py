"""
URLConf for Satchmo Contacts.
"""

from django.conf.urls.defaults import *

urlpatterns = patterns('satchmo.contact.views',
    (r'^$', 'view', {}, 'satchmo_account_info'),
    (r'^update/$', 'update', {}, 'satchmo_profile_update'), 
)
