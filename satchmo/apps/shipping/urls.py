from django.conf.urls.defaults import *

#Urls which need to be loaded at root level.
adminpatterns = patterns('',
    (r'^admin/print/(?P<doc>[-\w]+)/(?P<id>\d+)', 
        'shipping.views.displayDoc', {}, 
        'satchmo_print_shipping'),
)
