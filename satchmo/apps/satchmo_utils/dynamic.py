from django.contrib.sites.models import Site
from django.core import urlresolvers
from satchmo_utils import url_join
from django.contrib.sites.models import Site
import logging
log = logging.getLogger('satchmo_utils')

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
            possible = settings.KEY.value + "_" + name
            url = urlresolvers.reverse(possible)
        except urlresolvers.NoReverseMatch:
            log.debug('No url found for %s', possible)

    if not url:
        try:
            url = urlresolvers.reverse(name)
        except urlresolvers.NoReverseMatch:
            log.error('Could not find any url for %s', name)
            raise urlresolvers.NoReverseMatch('No reverse for %s or %s' % (possible, name))
            
    if include_server:
        if ssl:
            method = "https://"
        else:
            method = "http://"
        site = Site.objects.get_current()
        url = url_join(method, site.domain, url)

    return url
