from django.conf.urls.defaults import *
from django.contrib.sites.models import Site
from django.core import urlresolvers
from satchmo.configuration import config_get_group, config_get, config_value
from satchmo.shop.utils import load_module, url_join
import logging

log = logging.getLogger('payment.urls')

config = config_get_group('PAYMENT')

urlpatterns = patterns('satchmo.payment.views',
     (r'^$', 'contact_info', {'SSL': config.SSL.value}, 'satchmo_checkout-step1'),
     (r'custom/charge/(?P<orderitem_id>\d+)/$', 'charge_remaining', {}, 'satchmo_charge_remaining'),
     (r'custom/charge/$', 'charge_remaining_post', {}, 'satchmo_charge_remaining_post'),
     (r'^balance/$', 'balance_remaining', {'SSL' : config.SSL.value}, 'satchmo_balance_remaining')
)

# now add all enabled module payment settings

def make_urlpatterns():
    patterns = []
    for key in config_value('PAYMENT', 'MODULES'):
        cfg = config_get(key, 'MODULE')
        modulename = cfg.editor_value
        urlmodule = "%s.urls" % modulename
        patterns.append(url(config_value(key, 'URL_BASE'), [urlmodule]))
    return tuple(patterns)
    
urlpatterns += make_urlpatterns()

# --- Helper functions ---

def lookup_template(settings, template):
    """Return a template name, which may have been overridden in the settings."""

    if settings.has_key('TEMPLATE_OVERRIDES'):
        val = settings['TEMPLATE_OVERRIDES']
        template = val.get(template, template)

    return template

def lookup_url(settings, name, include_server=False, ssl=False):
    """Look up a named URL for the payment module.

    Tries a specific-to-general lookup fallback, returning
    the first positive hit.

    First look for a dictionary named "URL_OVERRIDES" on the settings object.
    Next try prepending the module name to the name
    Last just look up the name
    """
    url = None

    if settings.has_key('URL_OVERRIDES'):
        val = settings['URL_OVERRIDES']
        url = val.get(name, None)

    if not url:
        try:
            url = urlresolvers.reverse(settings.KEY.value + "_" + name)
        except urlresolvers.NoReverseMatch:
            pass

    if not url:
        url = urlresolvers.reverse(name)

    if include_server:
        if ssl:
            method = "https://"
        else:
            method = "http://"
        site = Site.objects.get_current()
        url = url_join(method, site.domain, url)

    return url
