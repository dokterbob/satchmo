"""
URLConf for Satchmo Contacts.
"""

from django.conf.urls.defaults import *
from signals_ahoy.signals import collect_urls
from satchmo_store import contact

urlpatterns = patterns('satchmo_store.contact.views',
    (r'^$', 'view', {}, 'satchmo_account_info'),
    (r'^update/$', 'update', {}, 'satchmo_profile_update'), 
)

collect_urls.send(sender=contact, patterns=urlpatterns)