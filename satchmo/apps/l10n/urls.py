from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^setlang/$', 'django.views.i18n.set_language', {}, 'satchmo_set_language'),
)
