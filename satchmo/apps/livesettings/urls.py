from django.conf.urls.defaults import *

urlpatterns = patterns('livesettings.views',
    (r'^$', 'site_settings', {}, 'satchmo_site_settings'),
    (r'^(?P<group>[^/]+)/$', 'group_settings'),
)
