import logging
from product.models import ConfigurableProduct

class LogMiddleware(object):
    """
    This middleware setups a cache to store information on which items are
    viewed.
    """
    def process_view(self, request, view_func, view_args, view_kwargs):
        logger1 = logging.getLogger('stats')
        if 'slug' in view_kwargs and 'queryset' in view_kwargs:
            try:
                if isinstance(view_kwargs['queryset'][0], ConfigurableProduct):
                    logger1.info("Viewing item %s" % view_kwargs['slug'])
            except IndexError:
                pass
        return None
