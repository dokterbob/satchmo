# -*- coding: UTF-8 -*-
from django.http import Http404
import keyedcache
import random
from django.test import TestCase
import re
import time

CACHE_HIT=0

def cachetest(a,b,c):
    global CACHE_HIT
    CACHE_HIT += 1
    r = [random.randrange(0,1000) for x in range(0,3)]
    ret = [r, a + r[0], b + r[1], c + r[2]]
    return ret

cachetest = keyedcache.cache_function(2)(cachetest)
    
class DecoratorTest(TestCase):
    
    def testCachePut(self):
        d = cachetest(1,2,3)
        self.assertEqual(CACHE_HIT,1)
        
        d2 = cachetest(1,2,3)
        self.assertEqual(CACHE_HIT,1)
        self.assertEqual(d, d2)

        seeds = d[0]
        self.assertEqual(seeds[0] + 1, d[1])
        self.assertEqual(seeds[1] + 2, d[2])
        self.assertEqual(seeds[2] + 3, d[3])
        
        time.sleep(3)
        d3 = cachetest(1,2,3)
        self.assertEqual(CACHE_HIT,2)
        self.assertNotEqual(d, d3)
        
    def testDeleteCachedFunction(self):
        orig = cachetest(10,20,30)
        keyedcache.cache_delete_function(cachetest)
        after = cachetest(10,20,30)
        self.assertNotEqual(orig,keyedcache)

class CachingTest(TestCase):
    
    def testCacheGetFail(self):
        try:
            keyedcache.cache_get('x')
            self.fail('should have raised NotCachedError')
        except keyedcache.NotCachedError:
            pass
            
    def testCacheGetOK(self):
        one = [1,2,3,4]
        keyedcache.cache_set('ok', value=one, length=2)
        two = keyedcache.cache_get('ok')
        self.assertEqual(one, two)
        
        time.sleep(5)
        try:
            three = keyedcache.cache_get('ok')
            self.fail('should have raised NotCachedError, got %s' % three)
        except keyedcache.NotCachedError:
            pass
        
    def testCacheGetDefault(self):
        chk = keyedcache.cache_get('default',default='-')
        self.assertEqual(chk, '-')


    def testDelete(self):
        keyedcache.cache_set('del', value=True)
        
        for x in range(0,10):
            keyedcache.cache_set('del', 'x', x, value=True)
            for y in range(0,5):
                keyedcache.cache_set('del', 'x', x, 'y', y, value=True)

        # check to make sure all the values are in the cache
        self.assert_(keyedcache.cache_get('del', default=False))
        for x in range(0,10):
            self.assert_(keyedcache.cache_get('del', 'x', x, default=False))
            for y in range(0,5):
                self.assert_(keyedcache.cache_get('del', 'x', x, 'y', y, default=False))

        # try to delete just one
        killed = keyedcache.cache_delete('del','x',1)
        self.assertEqual([keyedcache.CACHE_PREFIX + "::del::x::1"], killed)
        self.assertFalse(keyedcache.cache_get('del', 'x', 1, default=False))
        
        # but the others are still there
        self.assert_(keyedcache.cache_get('del', 'x', 2, default=False))

        # now kill all of del::x::1
        killed = keyedcache.cache_delete('del','x', 1, children=True)
        for y in range(0,5):
            self.assertFalse(keyedcache.cache_get('del', 'x', 1, 'y', y, default=False))
        
        # but del::x::2 and children are there
        self.assert_(keyedcache.cache_get('del','x',2,'y',1, default=False))
        
        # kill the rest
        killed = keyedcache.cache_delete('del', children=True)
        self.assertFalse(keyedcache.cache_get('del',default=False))
        for x in range(0,10):
            self.assertFalse(keyedcache.cache_get('del', 'x', x, default=False))
            for y in range(0,5):
                self.assertFalse(keyedcache.cache_get('del', 'x', x, 'y', y, default=False))


class TestCacheDisable(TestCase):
    
    def testDisable(self):
        keyedcache.cache_set('disabled', value=False)
        v = keyedcache.cache_get('disabled')
        self.assertEqual(v, False)
        
        keyedcache.cache_enable(False)
        keyedcache.cache_set('disabled', value=True)
        try:
            keyedcache.cache_get('disabled')
            self.fail('should have raised NotCachedError')
        except keyedcache.NotCachedError, nce:
            key = keyedcache.cache_key('disabled')
            self.assertEqual(nce.key, key)
            
        keyedcache.cache_enable()
        v2 = keyedcache.cache_get('disabled')
        # should still be False, since the cache was disabled
        self.assertEqual(v2, False)

class TestKeyMaker(TestCase):
    
    def testSimpleKey(self):
        v = keyedcache.cache_key('test')
        self.assertEqual(v, keyedcache.CACHE_PREFIX + '::test')
        
    def testDualKey(self):
        v = keyedcache.cache_key('test', 2)
        self.assertEqual(v, keyedcache.CACHE_PREFIX + '::test::2')

    def testPairedKey(self):
        v = keyedcache.cache_key('test', more='yes')
        self.assertEqual(v, keyedcache.CACHE_PREFIX + '::test::more::yes')
        
    def testPairedDualKey(self):
        v = keyedcache.cache_key('test', 3, more='yes')
        self.assertEqual(v, keyedcache.CACHE_PREFIX + '::test::3::more::yes')


        
