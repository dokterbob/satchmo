"""
URLConf for Satchmo Newsletter app

This will get automatically added by satchmo_store, under the url given in your livesettings "NEWSLETTER","NEWSLETTER_SLUG"
"""

from django.conf.urls.defaults import *
from livesettings import config_value
import logging
log = logging.getLogger('newsletter.urls')

urlpatterns = patterns('satchmo_ext.newsletter.views',
    (r'^subscribe/$', 'add_subscription', {}, 'newsletter_subscribe'),
    (r'^subscribe/ajah/$', 'add_subscription', 
        {'result_template' : 'newsletter/ajah.html'}, 'newsletter_subscribe_ajah'),
    (r'^unsubscribe/$', 'remove_subscription', 
        {}, 'newsletter_unsubscribe'),
    (r'^unsubscribe/ajah/$', 'remove_subscription', 
        {'result_template' : 'newsletter/ajah.html'}, 'newsletter_unsubscribe_ajah'),
    (r'^update/$', 'update_subscription', {}, 'newsletter_update'),
)

newsbase = r'^' + config_value('NEWSLETTER','NEWSLETTER_SLUG') + '/'    
newspatterns = patterns('',
    (newsbase, include('satchmo_ext.newsletter.urls'))
)

def add_newsletter_urls(sender, patterns=(), **kwargs):
    log.debug("Adding newsletter urls at %s", newsbase)
    patterns += newspatterns
