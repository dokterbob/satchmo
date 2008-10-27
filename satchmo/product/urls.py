from django.conf.urls.defaults import *

urlpatterns = patterns('satchmo.product.views',
    (r'^product/(?P<product_slug>[-\w]+)/$', 
        'get_product', {}, 'satchmo_product'),
    (r'^product/(?P<product_slug>[-\w]+)/prices/$', 
        'get_price', {}, 'satchmo_product_prices'),
    (r'^product/(?P<product_slug>[-\w]+)/price_detail/$', 
        'get_price_detail', {}, 'satchmo_product_price_detail'),
    (r'^category/(?P<parent_slugs>[-\w]+/)*(?P<slug>[-\w]+)/$', 
        'category_view', {}, 'satchmo_category'),
    (r'^category/$', 'category_index', {}, 'satchmo_category_index'),
)

urlpatterns += patterns('satchmo.product.filterviews',
    (r'^product/view/recent/$', 
        'display_recent', {}, 'satchmo_product_recently_added'),
    (r'^product/view/bestrated/$', 
        'display_bestratings', {}, 'satchmo_product_best_rated'),
    (r'^product/view/bestsellers/$', 
        'display_bestsellers', {}, 'satchmo_product_best_selling'),
)

urlpatterns += patterns('satchmo.product.adminviews',
    (r'^product/inventory/edit/$', 
        'edit_inventory', {}, 'satchmo_admin_edit_inventory'),
    (r'^product/inventory/export/$',
        'export_products', {}, 'satchmo_admin_product_export'),
    (r'^product/inventory/import/$', 
        'import_products', {}, 'satchmo_admin_product_import'),
    (r'^product/inventory/report/$', 
        'product_active_report', {}, 'satchmo_admin_product_report'),
    (r'^product/admin/(?P<product_slug>[-\w]+)/variations/$', 
        'variation_manager', {}, 'satchmo_admin_variation_manager'),
    (r'^product/admin/variations/$', 
        'variation_list', {}, 'satchmo_admin_variation_list'),
)
