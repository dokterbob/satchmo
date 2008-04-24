from django.core import urlresolvers
from satchmo.configuration import config_value
import logging
import re

log = logging.getLogger('recentlist.middleware')

producturl = urlresolvers.reverse('satchmo_product', None,('FAKE',))
producturl = "^" + producturl.replace("FAKE", r'(?P<slug>[-\w]+)')
log.debug('product url is %s', producturl)

urlre = re.compile(producturl)

class RecentProductMiddleware(object):
    """Remember recent products"""
    def process_response(self, request, response):
        g = urlre.search(request.path)
        if g and len(g.groups()) > 0 and "/admin/" not in request.path:
            recentmax = config_value('SHOP','RECENT_MAX')+1
            slug = g.groups()[0]
            recent = request.session.get('RECENTLIST',[])
            if slug not in recent:
                recent.insert(0, slug)
                if len(recent) > recentmax:
                    recent = recent[:recentmax]
                log.debug('Added recently viewed: %s', recent)
                request.session['RECENTLIST'] = recent
            
        return response