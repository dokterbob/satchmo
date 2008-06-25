from django import template
from django.utils.safestring import mark_safe
from satchmo.shop.templatetags import get_filter_args
from satchmo.shop import utils
from satchmo.shop.utils.json import json_encode

register = template.Library()

def template_range(value):
    """Return a range 1..value"""
    return range(1, value + 1)
    
register.filter('template_range', template_range)

def in_list(value, val=None):
    """returns "true" if the value is in the list"""
    if val in value:
        return "true"
    return ""
    
register.filter('in_list', in_list)

def app_enabled(value):
    """returns "true" if the app is enabled"""
    if utils.app_enabled(value):
        return "true"
    else:
        return ""
    
register.filter('app_enabled', app_enabled)

def as_json(value):
    """Return the value as a json encoded object"""
    return mark_safe(json_encode(value))
    
register.filter('as_json', as_json)

def truncate_decimal(val, places=2):
    return utils.trunc_decimal(val, places)
    
register.filter('truncate_decimal', truncate_decimal)

def remove_tags(value):
    """
    Returns the text with all tags removed
    This can fail if give invalid input. This is only intended to be used on safe HTML markup. It should not be used to 
    clean unsafe input data.
    For example, this will fail:
    >> remove_tags('<<> <test></test>')
        '<test></test>'
    """
    i = value.find('<')
    last = -1
    out = []
    if i == -1:
        return value
            
    while i>-1:
        out.append(value[last+1:i])
        last = value.find(">", i)
        if last > -1:
            i = value.find("<", last)
        else:
            break

    if last > -1:
        out.append(value[last+1:])
    
    ret = " ".join(out)
    ret = ret.replace("  ", " ")
    ret = ret.replace("  ", " ")
    if ret.endswith(" "):
        ret = ret[:-1]
    return ret
    
register.filter('remove_tags', remove_tags)

def lookup(value, key):
    """
    Return a dictionary lookup of key in value
    """
    try:
        return value[key]
    except KeyError:
        return ""
        
register.filter('lookup', lookup)

def is_mod(value, args=""):
    try:
        val = int(value)
        mod = int(args)
        if val%mod == 0:
            return "true"
    except:
        pass
        
    return ""

register.filter('is_mod', is_mod)

def more_than(value, args=""):
    try:
        val = int(value)
        more = int(args)
        if val > more:
            return "true"
    except:
        pass
        
    return ""
    
register.filter('more_than', more_than)
