# -*- coding: UTF-8 -*-
from django.http import Http404
from satchmo import caching
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

cachetest = caching.cache_function(2)(cachetest)
    
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
        caching.cache_delete_function(cachetest)
        after = cachetest(10,20,30)
        self.assertNotEqual(orig,caching)

class CachingTest(TestCase):
    
    def testCacheGetFail(self):
        try:
            caching.cache_get('x')
            self.fail('should have raised NotCachedError')
        except caching.NotCachedError:
            pass
            
    def testCacheGetOK(self):
        one = [1,2,3,4]
        caching.cache_set('ok', value=one, length=2)
        two = caching.cache_get('ok')
        self.assertEqual(one, two)
        
        time.sleep(5)
        try:
            three = caching.cache_get('ok')
            self.fail('should have raised NotCachedError, got %s' % three)
        except caching.NotCachedError:
            pass
        
    def testCacheGetDefault(self):
        chk = caching.cache_get('default',default='-')
        self.assertEqual(chk, '-')


    def testDelete(self):
        caching.cache_set('del', value=True)
        
        for x in range(0,10):
            caching.cache_set('del', 'x', x, value=True)
            for y in range(0,5):
                caching.cache_set('del', 'x', x, 'y', y, value=True)

        # check to make sure all the values are in the cache
        self.assert_(caching.cache_get('del', default=False))
        for x in range(0,10):
            self.assert_(caching.cache_get('del', 'x', x, default=False))
            for y in range(0,5):
                self.assert_(caching.cache_get('del', 'x', x, 'y', y, default=False))

        # try to delete just one
        killed = caching.cache_delete('del','x',1)
        self.assertEqual([caching.CACHE_PREFIX + "::del::x::1"], killed)
        self.assertFalse(caching.cache_get('del', 'x', 1, default=False))
        
        # but the others are still there
        self.assert_(caching.cache_get('del', 'x', 2, default=False))

        # now kill all of del::x::1
        killed = caching.cache_delete('del','x', 1, children=True)
        for y in range(0,5):
            self.assertFalse(caching.cache_get('del', 'x', 1, 'y', y, default=False))
        
        # but del::x::2 and children are there
        self.assert_(caching.cache_get('del','x',2,'y',1, default=False))
        
        # kill the rest
        killed = caching.cache_delete('del', children=True)
        self.assertFalse(caching.cache_get('del',default=False))
        for x in range(0,10):
            self.assertFalse(caching.cache_get('del', 'x', x, default=False))
            for y in range(0,5):
                self.assertFalse(caching.cache_get('del', 'x', x, 'y', y, default=False))


class TestKeyMaker(TestCase):
    
    def testSimpleKey(self):
        v = caching.cache_key('test')
        self.assertEqual(v, caching.CACHE_PREFIX + '::test')
        
    def testDualKey(self):
        v = caching.cache_key('test', 2)
        self.assertEqual(v, caching.CACHE_PREFIX + '::test::2')

    def testPairedKey(self):
        v = caching.cache_key('test', more='yes')
        self.assertEqual(v, caching.CACHE_PREFIX + '::test::more::yes')
        
    def testPairedDualKey(self):
        v = caching.cache_key('test', 3, more='yes')
        self.assertEqual(v, caching.CACHE_PREFIX + '::test::3::more::yes')


        
