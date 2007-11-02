"""
URLConf for Caching app
"""

from django.conf.urls.defaults import *

urlpatterns = patterns('satchmo.caching.views',
    (r'^$', 'stats_page', {}, 'caching_stats'),
    (r'^view/$', 'view_page', {}, 'caching_view'),
    (r'^delete/$', 'delete_page', {}, 'caching_delete'),
)
