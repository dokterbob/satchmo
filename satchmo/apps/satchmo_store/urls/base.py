"""Base urls used by Satchmo.

Split out from urls.py to allow much easier overriding and integration with larger apps.
"""
from django.conf.urls.defaults import *
from satchmo_store.shop import get_satchmo_setting
from satchmo_utils.signals import collect_urls
from product.urls.base import adminpatterns as prodpatterns
from shipping.urls import adminpatterns as shippatterns
import logging
import satchmo_store

log = logging.getLogger('shop.urls')

urlpatterns = patterns('',
    (r'^admin/doc/', include('django.contrib.admindocs.urls')),
    (r'^accounts/', include('satchmo_store.accounts.urls')),
    (r'^settings/', include('livesettings.urls')),
    (r'^cache/', include('keyedcache.urls')),
) + prodpatterns + shippatterns

collect_urls.send(sender=satchmo_store, patterns=urlpatterns)