"""A full cache system written on top of Django's rudimentary one."""

from django.conf import settings
from django.core.cache import cache
from django.utils.encoding import smart_str
from django.utils.hashcompat import md5_constructor
from satchmo_utils import is_string_like, is_list_or_tuple
import cPickle as pickle
import logging
import types

log = logging.getLogger('keyedcache')

CACHED_KEYS = {}
CACHE_CALLS = 0
CACHE_HITS = 0
KEY_DELIM = "::"
REQUEST_CACHE = {'enabled' : False}
try:
    CACHE_PREFIX = settings.CACHE_PREFIX
except AttributeError:
    CACHE_PREFIX = str(settings.SITE_ID)
    log.warn("No CACHE_PREFIX found in settings, using SITE_ID.  Please update your settings to add a CACHE_PREFIX")

try:
    CACHE_TIMEOUT = settings.CACHE_TIMEOUT
except AttributeError:
    CACHE_TIMEOUT = 0
    log.warn("No CACHE_TIMEOUT found in settings, so we used 0, disabling the cache system.  Please update your settings to add a CACHE_TIMEOUT and avoid this warning.")

_CACHE_ENABLED = CACHE_TIMEOUT > 0

class CacheWrapper(object):
    def __init__(self, val, inprocess=False):
        self.val = val
        self.inprocess = inprocess

    def __str__(self):
        return str(self.val)

    def __repr__(self):
        return repr(self.val)

    def wrap(cls, obj):
        if isinstance(obj, cls):
            return obj
        else:
            return cls(obj)

    wrap = classmethod(wrap)

class MethodNotFinishedError(Exception): 
    def __init__(self, f):
        self.func = f


class NotCachedError(Exception):    
    def __init__(self, k):
        self.key = k

class CacheNotRespondingError(Exception):    
    pass
    
def cache_delete(*keys, **kwargs):
    removed = []
    if cache_enabled():
        global CACHED_KEYS
        log.debug('cache_delete')
        children = kwargs.pop('children',False)

        if (keys or kwargs):
            key = cache_key(*keys, **kwargs)
    
            if CACHED_KEYS.has_key(key):
                del CACHED_KEYS[key]
                removed.append(key)

            cache.delete(key)

            if children:
                key = key + KEY_DELIM
                children = [x for x in CACHED_KEYS.keys() if x.startswith(key)]
                for k in children:
                    del CACHED_KEYS[k]
                    cache.delete(k)
                    removed.append(k)
        else:
            key = "All Keys"
            deleteneeded = _cache_flush_all()
        
            removed = CACHED_KEYS.keys()

            if deleteneeded:
                for k in CACHED_KEYS:
                    cache.delete(k)
            
            CACHED_KEYS = {}

        if removed:
            log.debug("Cache delete: %s", removed)
        else:
            log.debug("No cached objects to delete for %s", key)

    return removed


def cache_delete_function(func):
    return cache_delete(['func', func.__name__, func.__module__], children=True)

def cache_enabled():
    global _CACHE_ENABLED
    return _CACHE_ENABLED

def cache_enable(state=True):
    global _CACHE_ENABLED
    _CACHE_ENABLED=state

def _cache_flush_all():
    if is_memcached_backend():
        cache._cache.flush_all()
        return False
    return True

def cache_function(length=CACHE_TIMEOUT):
    """
    A variant of the snippet posted by Jeff Wheeler at
    http://www.djangosnippets.org/snippets/109/

    Caches a function, using the function and its arguments as the key, and the return
    value as the value saved. It passes all arguments on to the function, as
    it should.

    The decorator itself takes a length argument, which is the number of
    seconds the cache will keep the result around.

    It will put a temp value in the cache while the function is
    processing. This should not matter in most cases, but if the app is using
    threads, you won't be able to get the previous value, and will need to
    wait until the function finishes. If this is not desired behavior, you can
    remove the first two lines after the ``else``.
    """
    def decorator(func):
        def inner_func(*args, **kwargs):
            if not cache_enabled():
                value = func(*args, **kwargs)
                
            else:        
                try:
                    value = cache_get('func', func.__name__, func.__module__, args, kwargs)

                except NotCachedError, e:
                    # This will set a temporary value while ``func`` is being
                    # processed. When using threads, this is vital, as otherwise
                    # the function can be called several times before it finishes
                    # and is put into the cache.
                    funcwrapper = CacheWrapper(".".join([func.__module__, func.__name__]), inprocess=True)
                    cache_set(e.key, value=funcwrapper, length=length, skiplog=True)
                    value = func(*args, **kwargs)
                    cache_set(e.key, value=value, length=length)
                
                except MethodNotFinishedError, e:
                    value = func(*args, **kwargs)

            return value
        return inner_func
    return decorator


def cache_get(*keys, **kwargs):
    if kwargs.has_key('default'):
        default_value = kwargs.pop('default')
        use_default = True
    else:
        use_default = False

    key = cache_key(keys, **kwargs)
    
    if not cache_enabled():
        raise NotCachedError(key)
    else:
        global CACHE_CALLS, CACHE_HITS, REQUEST_CACHE
        CACHE_CALLS += 1
        if CACHE_CALLS == 1:
            cache_require()
        
        obj = None
        tid = -1
        if REQUEST_CACHE['enabled']:
            tid = cache_get_request_uid()
            if tid > -1:
                try:
                    obj = REQUEST_CACHE[tid][key]
                    log.debug('Got from request cache: %s', key)
                except KeyError:
                    pass

        if obj == None:
            obj = cache.get(key)
            
        if obj and isinstance(obj, CacheWrapper):
            CACHE_HITS += 1
            CACHED_KEYS[key] = True
            log.debug('got cached [%i/%i]: %s', CACHE_CALLS, CACHE_HITS, key)
            if obj.inprocess:
                raise MethodNotFinishedError(obj.val)
            
            cache_set_request(key, obj, uid=tid)
            
            return obj.val
        else:
            try:
                del CACHED_KEYS[key]
            except KeyError:
                pass

            if use_default:
                return default_value
    
            raise NotCachedError(key)


def cache_set(*keys, **kwargs):
    """Set an object into the cache."""
    if cache_enabled():
        global CACHED_KEYS, REQUEST_CACHE
        obj = kwargs.pop('value')
        length = kwargs.pop('length', CACHE_TIMEOUT)
        skiplog = kwargs.pop('skiplog', False)

        key = cache_key(keys, **kwargs)
        val = CacheWrapper.wrap(obj)
        if not skiplog:
            log.debug('setting cache: %s', key)
        cache.set(key, val, length)
        CACHED_KEYS[key] = True
        if REQUEST_CACHE['enabled']:
            cache_set_request(key, val)

def _hash_or_string(key):
    if is_string_like(key) or isinstance(key, (types.IntType, types.LongType, types.FloatType)):
        return smart_str(key)
    else:
        try:
            #if it has a PK, use it.
            return str(key._get_pk_val())
        except AttributeError:
            return md5_hash(key)

def cache_contains(*keys, **kwargs):
    key = cache_key(keys, **kwargs)
    return CACHED_KEYS.has_key(key)

def cache_key(*keys, **pairs):
    """Smart key maker, returns the object itself if a key, else a list 
    delimited by ':', automatically hashing any non-scalar objects."""

    if is_string_like(keys):
        keys = [keys]
        
    if is_list_or_tuple(keys):
        if len(keys) == 1 and is_list_or_tuple(keys[0]):
            keys = keys[0]
    else:
        keys = [md5_hash(keys)]

    if pairs:
        keys = list(keys)
        klist = pairs.keys()
        klist.sort()
        for k in klist:
            keys.append(k)
            keys.append(pairs[k])
    
    key = KEY_DELIM.join([_hash_or_string(x) for x in keys])
    prefix = CACHE_PREFIX + KEY_DELIM
    if not key.startswith(prefix):
        key = prefix+key
    return key.replace(" ", ".")

def md5_hash(obj):
    pickled = pickle.dumps(obj, protocol=pickle.HIGHEST_PROTOCOL)
    return md5_constructor(pickled).hexdigest()


def is_memcached_backend():
    try:
        return cache._cache.__module__.endswith('memcache')
    except AttributeError:
        return False

def cache_require():
    """Error if keyedcache isn't running."""
    if cache_enabled():
        key = cache_key('require_cache')
        cache_set(key,value='1')
        v = cache_get(key, default = '0')
        if v != '1':
            raise CacheNotRespondingError()
        else:
            log.debug("Cache responding OK")
        return True

def cache_clear_request(uid):
    """Clears all locally cached elements with that uid"""
    global REQUEST_CACHE
    try:
        del REQUEST_CACHE[uid]
        log.debug('cleared request cache: %s', uid)
    except KeyError:
        pass

def cache_use_request_caching():
    global REQUEST_CACHE
    REQUEST_CACHE['enabled'] = True

def cache_get_request_uid():
    from threaded_multihost import threadlocals
    return threadlocals.get_thread_variable('request_uid', -1)
    
def cache_set_request(key, val, uid=None):
    if uid == None:
        uid = cache_get_request_uid()

    if uid>-1:
        global REQUEST_CACHE
        if not uid in REQUEST_CACHE:
            REQUEST_CACHE[uid] = {key:val}
        else:
            REQUEST_CACHE[tid][key] = val
