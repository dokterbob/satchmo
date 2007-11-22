# -*- coding: UTF-8 -*-
from decimal import Decimal
from django.core import urlresolvers
from django.test import TestCase
#from models import GiftCertificate
from satchmo.configuration import config_get_group, config_value
from urls import lookup_template, lookup_url, make_urlpatterns
#from modules.giftcertificate.utils import generate_certificate_code, generate_code

alphabet = 'abcdefghijklmnopqrstuvwxyz'

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

# class TestGenerateCode(TestCase):
# 
#     def testGetCode(self):
#         c = generate_code(alphabet, '^^^^')
# 
#         self.assertEqual(len(c), 4)
# 
#         for ch in c:
#             self.assert_(ch in alphabet)
# 
#     def testGetCode2(self):
#         c = generate_code(alphabet, '^^^^-^^^^')
#         c2 = generate_code(alphabet, '^^^^-^^^^')
#         self.assertNotEqual(c,c2)
# 
#     def testFormat(self):
#         c = generate_code(alphabet, '^-^-^-^')
#         for i in (0,2,4,6):
#             self.assert_(c[i] in alphabet)
#         for i in (1,3,5):
#             self.assertEqual(c[i], '-')

# class TestGenerateCertificateCode(TestCase):
#     def setUp(self):
#         self.charset = config_value('PAYMENT_GIFTCERTIFICATE', 'CHARSET')
#         self.format = config_value('PAYMENT_GIFTCERTIFICATE', 'FORMAT')
# 
#     def testGetCode(self):
#         c = generate_certificate_code()
#         self.assertEqual(len(c), len(self.format))
# 
#         chars = [x for x in self.format if not x=='^']
#         chars.extend(self.charset)
#         for ch in c:
#             self.assert_(ch in chars)
# 
# class TestCertCreate(TestCase):
#     def testCreate(self):
#         gc = GiftCertificate(start_balance = '100.00')
#         gc.save()
# 
#         self.assert_(gc.code)
#         self.assertEqual(gc.balance, Decimal('100.00'))
# 
#     def testUse(self):
#         gc = GiftCertificate(start_balance = '100.00')
#         gc.save()
#         bal = gc.use('10.00')
#         self.assertEqual(bal, Decimal('90.00'))
#         self.assertEqual(gc.usages.count(), 1)

