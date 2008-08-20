from django import template
from satchmo.shop.utils import is_multihost_enabled
from satchmo.shop.models import Config
from satchmo.utils import url_join
from django.core import urlresolvers

register = template.Library()

def admin_site_views(view):
    """Returns a formatted list of sites, rendering for view, if any"""
    
    configs = Config.objects.all()
    if view:
        path = urlresolvers.reverse(view)
    else:
        path = None

    links = []
    for config in configs:
        paths = ["http://", config.site.domain]
        if path:
            paths.append(path)
            
        links.append((config.store_name, url_join(paths)))
    
    ret = {
        'links' : links,
        'multihost' : is_multihost_enabled()
    }
    print ret
    return ret
    

register.inclusion_tag('admin/_admin_site_views.html')(admin_site_views)
