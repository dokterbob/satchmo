"""
URLConf for Satchmo Newsletter app

Recommended usage is to use a call to ``include()`` in your project's
root URLConf to include this URLConf for any URL beginning with
'/newsletter/'.

"""

from django.conf.urls.defaults import *

urlpatterns = patterns('satchmo.newsletter.views',
    (r'^subscribe/$', 'add_subscription', {}, 'newsletter_subscribe'),
    (r'^subscribe/ajah/$', 'add_subscription', {'result_template' : 'newsletter/ajah.html'}, 'newsletter_subscribe_ajah'),
    (r'^unsubscribe/$', 'remove_subscription', {}, 'newsletter_unsubscribe'),
    (r'^unsubscribe/ajah/$', 'remove_subscription', {'result_template' : 'newsletter/ajah.html'}, 'newsletter_unsubscribe_ajah'),
    (r'^update/$', 'update_subscription', {}, 'newsletter_update'),
)
