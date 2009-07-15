from django.conf.urls.defaults import *

urlpatterns = patterns('livesettings.views',
    (r'^$', 'site_settings', {}, 'satchmo_site_settings'),
    (r'^export/$', 'export_as_python', {}, 'settings_export'),
    (r'^(?P<group>[^/]+)/$', 'group_settings'),
)
