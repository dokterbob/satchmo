from django.conf.urls.defaults import *

urlpatterns = patterns('satchmo.product.brand.views',
    (r'^$', 'brand_list', {}, 'satchmo_brand_list'),
    (r'^(?P<brandname>.*)/(?P<catname>.*)/$', 'brand_category_page', {}, 'satchmo_brand_category_view'),
    (r'^(?P<brandname>.*)/$', 'brand_page', {}, 'satchmo_brand_view'),
)
    
