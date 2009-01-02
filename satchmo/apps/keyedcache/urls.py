"""
URLConf for Caching app
"""

from django.conf.urls.defaults import *

urlpatterns = patterns('keyedcache.views',
    (r'^$', 'stats_page', {}, 'keyedcache_stats'),
    (r'^view/$', 'view_page', {}, 'keyedcache_view'),
    (r'^delete/$', 'delete_page', {}, 'keyedcache_delete'),
)
