from django.conf.urls.defaults import *

urlpatterns = patterns('product.views',
    (r'^(?P<parent_slugs>([-\w]+/)*)?(?P<slug>[-\w]+)/$',
        'category_view', {}, 'satchmo_category'),
    (r'^$', 'category_index', {}, 'satchmo_category_index'),
)
