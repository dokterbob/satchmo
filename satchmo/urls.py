from django.conf import settings
from django.conf.urls.defaults import *
from django.contrib import admin
from satchmo.utils import urlhelper
from satchmo.urls_base import urlpatterns as satchmopatterns
from django.contrib import admin
# discover all admin modules - if you override this for your
# own base URLs, you'll need to autodiscover there.
admin.autodiscover()

urlpatterns = getattr(settings, 'URLS', [])

if urlpatterns:
    urlpatterns += satchmopatterns
else:
    urlpatterns = satchmopatterns

urlpatterns += patterns('',
    (r'^admin/(.*)', admin.site.root),
)
    
#The following is used to serve up local media files like images
if getattr(settings, 'LOCAL_DEV', False):
    baseurlregex = r'^static/(?P<path>.*)$'
    urlpatterns += patterns('',
        (baseurlregex, 'django.views.static.serve',
        {'document_root':  settings.MEDIA_ROOT}),
    )

urlhelper.remove_duplicate_urls(urlpatterns, [])

