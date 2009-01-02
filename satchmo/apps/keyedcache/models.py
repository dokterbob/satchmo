import keyedcache
import logging

log = logging.getLogger('keyedcache')

class CachedObjectMixin(object):
    """Provides basic object keyedcache for any objects using this as a mixin."""

    def cache_delete(self, *args, **kwargs):
        key = self.cache_key(*args, **kwargs)
        log.debug("clearing cache for %s", key)
        keyedcache.cache_delete(key, children=True)

    def cache_get(self, *args, **kwargs):
        key = self.cache_key(*args, **kwargs)
        return keyedcache.cache_get(key)

    def cache_key(self, *args, **kwargs):
        keys = [self.__class__.__name__, self]
        keys.extend(args)
        return keyedcache.cache_key(keys, **kwargs)

    def cache_reset(self):
        self.cache_delete()
        self.cache_set()

    def cache_set(self, *args, **kwargs):
        val = kwargs.pop('value', self)
        key = self.cache_key(*args, **kwargs)
        keyedcache.cache_set(key, value=val)
        
    def is_cached(self, *args, **kwargs):
        return keyedcache.is_cached(self.cache_key(*args, **kwargs))
        
def find_by_id(cls, groupkey, objectid, raises=False):
    """A helper function to look up an object by id"""
    ob = None
    try:
        ob = keyedcache.cache_get(groupkey, objectid)
    except keyedcache.NotCachedError, e:
        try: 
            ob = cls.objects.get(pk=objectid)
            keyedcache.cache_set(e.key, value=ob)

        except cls.DoesNotExist:
            log.debug("No such %s: %s", groupkey, objectid)
            if raises:
                raise cls.DoesNotExist

    return ob


def find_by_key(cls, groupkey, key, raises=False):
    """A helper function to look up an object by key"""
    ob = None
    try:
        ob = keyedcache.cache_get(groupkey, key)
    except keyedcache.NotCachedError, e:
        try: 
            ob = cls.objects.get(key__exact=key)
            keyedcache.cache_set(e.key, value=ob)

        except cls.DoesNotExist:
            log.debug("No such %s: %s", groupkey, key)
            if raises:
                raise

    return ob
    
def find_by_slug(cls, groupkey, slug, raises=False):
    """A helper function to look up an object by slug"""
    ob = None
    try:
        ob = keyedcache.cache_get(groupkey, slug)
    except keyedcache.NotCachedError, e:
        try: 
            ob = cls.objects.get(slug__exact=slug)
            keyedcache.cache_set(e.key, value=ob)

        except cls.DoesNotExist:
            log.debug("No such %s: %s", groupkey, slug)
            if raises:
                raise

    return ob

