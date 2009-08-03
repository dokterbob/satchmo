"""Urls which need to be loaded at root level."""
from django.conf.urls.defaults import *

adminpatterns = patterns('',
    (r'^admin/product/configurableproduct/(?P<id>\d+)/getoptions/', 
        'product.views.get_configurable_product_options', {}, 
        'satchmo_admin_configurableproduct'),
)

adminpatterns += patterns('product.views.adminviews',
    (r'^admin/inventory/edit/$', 
        'edit_inventory', {}, 'satchmo_admin_edit_inventory'),
    (r'^inventory/export/$',
        'export_products', {}, 'satchmo_admin_product_export'),
    (r'^inventory/import/$', 
        'import_products', {}, 'satchmo_admin_product_import'),
    # (r'^inventory/report/$', 
    #     'product_active_report', {}, 'satchmo_admin_product_report'),
    (r'^admin/(?P<product_id>\d+)/variations/$', 
        'variation_manager', {}, 'satchmo_admin_variation_manager'),
    (r'^admin/variations/$', 
        'variation_list', {}, 'satchmo_admin_variation_list'),
)
