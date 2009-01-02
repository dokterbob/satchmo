from django import template
from django.contrib.sites.models import Site
from django.core import urlresolvers
from livesettings import config_value, SettingNotSet
from satchmo_utils import url_join
import logging

log = logging.getLogger('configuration.config_tags')

register = template.Library()

def force_space(value, chars=40):
    """Forces spaces every `chars` in value"""

    chars = int(chars)
    if len(value) < chars:
        return value
    else:    
        out = []
        start = 0
        end = 0
        looping = True
        
        while looping:
            start = end
            end += chars
            out.append(value[start:end])
            looping = end < len(value)
    
    return ' '.join(out)

def break_at(value,  chars=40):
    """Force spaces into long lines which don't have spaces"""
    
    chars = int(chars)
    value = unicode(value)
    if len(value) < chars:
        return value
    else:
        out = []
        line = value.split(' ')
        for word in line:
            if len(word) > chars:
                out.append(force_space(word, chars))
            else:
                out.append(word)
                
    return " ".join(out)

register.filter('break_at', break_at)

def config_boolean(option):
    """Looks up the configuration option, returning true or false."""
    args = option.split('.')
    try:
        val = config_value(*args)
    except:
        log.warn('config_boolean tag: Tried to look up config setting "%s", got SettingNotSet, returning False', option)
        val = False
    if val:
        return "true"
    else:
        return ""

register.filter('config_boolean', config_boolean)

def admin_site_views(view):
    """Returns a formatted list of sites, rendering for view, if any"""

    if view:
        path = urlresolvers.reverse(view)
    else:
        path = None

    links = []
    for site in Site.objects.all():
        paths = ["http://", site.domain]
        if path:
            paths.append(path)
            
        links.append((site.name, url_join(paths)))
    
    ret = {
        'links' : links,
    }
    return ret
    

register.inclusion_tag('livesettings/_admin_site_views.html')(admin_site_views)
