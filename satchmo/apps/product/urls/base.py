"""Urls which need to be loaded at root level."""
from django.conf.urls.defaults import *

adminpatterns = patterns('',
    (r'^admin/product/configurableproduct/(?P<id>\d+)/getoptions/', 
        'product.views.get_configurable_product_options', {}, 
        'satchmo_admin_configurableproduct'),
)

