from django.conf.urls.defaults import *


urlpatterns = patterns('',
    (r'example/', 'large.localsite.views.example', {}),
)
