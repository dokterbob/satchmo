# -*- coding: UTF-8 -*-
from django.test import TestCase
from django.core import urlresolvers
from satchmo.configuration import config_get_group, config_value
from urls import lookup_template, lookup_url, make_urlpatterns

class TestModulesSettings(TestCase):

    def setUp(self):
        self.dummy = config_get_group('PAYMENT_DUMMY')

    def testGetDummy(self):
        self.assert_(self.dummy != None)
        self.assertEqual(self.dummy.LABEL, 'Payment test module')

    def testLookupTemplateSet(self):
        t = lookup_template(self.dummy, 'test.html')
        self.assertEqual(t, 'test.html')

        # TODO, add these back in when DictValues are added to Comfiguration
        #self.dummy['TEMPLATE_OVERRIDES'] = {'test2.html' : 'foo.html'}
        #t = lookup_template(self.dummy, 'test2.html')
        #self.assertEqual(t, 'foo.html')

    def testLookupURL(self):
        try:
            t = lookup_url(self.dummy, 'test_doesnt_exist')
            self.fail('Should have failed with NoReverseMatch')
        except urlresolvers.NoReverseMatch:
            pass

    def testUrlPatterns(self):
        pats = make_urlpatterns()
        self.assertTrue(len(pats) > 0)
