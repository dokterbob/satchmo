from decimal import Decimal, ROUND_HALF_UP, InvalidOperation
from django.conf import settings
import datetime
import logging
import os
import random
import sys
import types

log = logging.getLogger('shop.utils')

def add_month(date, n=1):
    """add n+1 months to date then subtract 1 day
    to get eom, last day of target month"""
    oneday = datetime.timedelta(days=1)
    q,r = divmod(date.month+n, 12)
    eom = datetime.date(date.year+q, r+1, 1) - oneday
    if date.month != (date+oneday).month or date.day >= eom.day:
        return eom
    return eom.replace(day=date.day)

def app_enabled(appname):
    """Check the app list to see if a named app is installed."""
    from django.db import models
    
    all_apps = {}
    for app in models.get_apps():
        n = app.__name__.split('.')[-2]
        if n  == appname:
            return True
    return False

def can_loop_over(maybe):
    """Test value to see if it is list like"""
    try:
        iter(maybe)
    except:
        return 0
    else:
        return 1

def cross_list(sequences):
    """
    Code taken from the Python cookbook v.2 (19.9 - Looping through the cross-product of multiple iterators)
    This is used to create all the variations associated with an product
    """
    result =[[]]
    for seq in sequences:
        result = [sublist+[item] for sublist in result for item in seq]
    return result

def current_media_url(request):    
    """Return the media_url, taking into account SSL."""
    media_url = settings.MEDIA_URL
    secure = request_is_secure(request)
    if secure:
        try:
            media_url = settings.MEDIA_SECURE_URL
        except AttributeError:
            media_url = media_url.replace('http://','https://')
    return media_url

def is_scalar(maybe):
    """Test to see value is a string, an int, or some other scalar type"""
    return is_string_like(maybe) or not can_loop_over(maybe)

def flatten_list(sequence, scalarp=is_scalar, result=None):
    """flatten out a list by putting sublist entries in the main list"""
    if result is None:
        result = []

    for item in sequence:
        if scalarp(item):
            result.append(item)
        else:
            flatten_list(item, scalarp, result)

def flatten(sequence, scalarp=is_scalar):
    """flatten out a list by putting sublist entries in the main list"""
    for item in sequence:
        if scalarp(item):
            yield item
        else:
            for subitem in flatten(item, scalarp):
                yield subitem

def get_flat_list(sequence):
    """flatten out a list and return the flat list"""
    flat = []
    flatten_list(sequence, result=flat)
    return flat

def is_list_or_tuple(maybe):
    return isinstance(maybe, (types.TupleType, types.ListType))

def is_string_like(maybe):
    """Test value to see if it acts like a string"""
    try:
        maybe+""
    except TypeError:
        return 0
    else:
        return 1

def load_module(module):
    """Load a named python module."""
    try:
        module = sys.modules[module]
    except KeyError:
        __import__(module)
        module = sys.modules[module]
    return module

_MODULES = []
def load_once(key, module):
    if key not in _MODULES:
        load_module(module)
        _MODULES.append(key)

def normalize_dir(dir_name):
    if not dir_name.startswith('./'):
        dir_name = url_join('.', dir_name)
    if dir_name.endswith("/"):
        dir_name = dir_name[:-1]
    return dir_name

_LETTERS = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"

def random_string(length, variable=False, charset=_LETTERS):
    if variable:
        length = random.randrange(1, length+1)
    return ''.join([random.choice(charset) for x in xrange(length)])

def request_is_secure(request):
    if request.is_secure():
        return True

    # Handle forwarded SSL (used at Webfaction)
    if 'HTTP_X_FORWARDED_SSL' in request.META:
        return request.META['HTTP_X_FORWARDED_SSL'] == 'on'

    # Handle an additional case of proxying SSL requests. This is useful for Media Temple's
    # Django container
    if 'HTTP_X_FORWARDED_HOST' in request.META and request.META['HTTP_X_FORWARDED_HOST'].endswith('443'):
        return True

    return False
            
def url_join(*args):
    """Join any arbitrary strings into a forward-slash delimited string.
    Do not strip leading / from first element, nor trailing / from last element.

    This function can take lists as arguments, flattening them appropriately.

    example:
    url_join('one','two',['three','four'],'five') => 'one/two/three/four/five'
    """
    if len(args) == 0:
        return ""

    args = get_flat_list(args)

    if len(args) == 1:
        return str(args[0])

    else:
        args = [str(arg).replace("\\", "/") for arg in args]

        work = [args[0]]
        for arg in args[1:]:
            if arg.startswith("/"):
                work.append(arg[1:])
            else:
                work.append(arg)

        joined = reduce(os.path.join, work)

    return joined.replace("\\", "/")
