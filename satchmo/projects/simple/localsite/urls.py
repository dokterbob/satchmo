from django.conf.urls.defaults import *


urlpatterns = patterns('',
    (r'example/', 'simple.localsite.views.example', {}),
)
