from django.core.urlresolvers import NoReverseMatch, reverse
from livesettings import config_value
import logging
import re

log = logging.getLogger('recentlist.middleware')

try:
    producturl = reverse('satchmo_product',
        kwargs={'product_slug': 'FAKE'})
    producturl = "^" + producturl.replace("FAKE", r'(?P<slug>[-\w]+)')
    log.debug('Product url is %s', producturl)
    urlre = re.compile(producturl)
except NoReverseMatch:
    log.debug("Could not find product url.")
    urlre = None

class RecentProductMiddleware(object):
    """Remember recent products"""
    def process_response(self, request, response):
        if urlre is not None: # If the product url was found earlier.
            g = urlre.search(request.path)
            if g and len(g.groups()) > 0 and "/admin/" not in request.path:
                recentmax = config_value('PRODUCT','RECENT_MAX') + 1
                slug = g.groups()[0]
                recent = request.session.get('RECENTLIST', [])
                if slug not in recent:
                    recent.insert(0, slug)
                    if len(recent) > recentmax:
                        recent = recent[:recentmax]
                    log.debug('Added recently viewed: %s', recent)
                    request.session['RECENTLIST'] = recent

        return response
