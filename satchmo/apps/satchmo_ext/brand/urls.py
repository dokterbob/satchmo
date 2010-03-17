"""
Urls for Product Brand module, note that you do not have to add this to your urls file, it will get automatically included by collect_urls.
"""
from django.conf.urls.defaults import *
from satchmo_store.shop import get_satchmo_setting
import logging

log = logging.getLogger('brand.urls')

urlpatterns = patterns('satchmo_ext.brand.views',
    (r'^$', 'brand_list', {}, 'satchmo_brand_list'),
    (r'^(?P<brandname>.*)/(?P<catname>.*)/$', 'brand_category_page', {}, 'satchmo_brand_category_view'),
    (r'^(?P<brandname>.*)/$', 'brand_page', {}, 'satchmo_brand_view'),
)

brandbase = r'^' + get_satchmo_setting('BRAND_SLUG') + '/'

prodbase = r'^' + get_satchmo_setting('PRODUCT_SLUG') + '/'
brandpatterns = patterns('',
    (brandbase, include('satchmo_ext.brand.urls'))
)

def add_brand_urls(sender, patterns=(), section="", **kwargs):
    if section=="__init__":
        log.debug('adding brand urls at %s', brandbase)
        patterns += brandpatterns
