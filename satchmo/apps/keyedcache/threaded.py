"""Causes the keyedcache to also use a first-level cache in memory - this can cut 30-40% of memcached calls.

To enable, add this to some models.py file in an app::

    from keyedcache import threaded
    threaded.start_listening()

"""
from threaded_multihost import threadlocals
from django.core.signals import request_started, request_finished
from keyedcache import cache_clear_request, cache_use_request_caching, cache_set_request_uid
import random
import logging
log = logging.getLogger('keyedcache.threaded')

def set_request_uid(sender, *args, **kwargs):
    """Puts a unique id into the thread"""
    tid = random.randrange(1,10000000)
    threadlocals.set_thread_variable('request_uid', tid)
    #log.debug('request UID: %s', tid)
    
def clear_request_uid(sender, *args, **kwargs):
    """Removes the thread cache for this request"""
    tid = threadlocals.get_thread_variable('request_uid', -1)
    if tid > -1:
        cache_clear_request(tid)
    
def start_listening():
    log.debug('setting up threaded keyedcache')
    cache_use_request_caching()
    request_started.connect(set_request_uid)
    request_finished.connect(clear_request_uid)
