# -*- coding: UTF-8 -*-
from decimal import Decimal
from django.core import urlresolvers
from django.test import TestCase
from django.test.client import Client
from django.conf import settings
#from models import GiftCertificate
from satchmo.configuration import config_get_group, config_value
from satchmo.shop.utils.dynamic import lookup_template, lookup_url
from urls import make_urlpatterns
#from modules.giftcertificate.utils import generate_certificate_code, generate_code
from satchmo.product.models import *
from satchmo.shop.models import *
from satchmo.contact.models import *

alphabet = 'abcdefghijklmnopqrstuvwxyz'

domain = 'http://testserver'
prefix = settings.SHOP_BASE
if prefix == '/':
    prefix = ''

class TestRecurringBilling(TestCase):
    fixtures = ['sub_products', 'config']

    def setUp(self):
        self.customer = Contact.objects.create(first_name='Jane', last_name='Doe')
        self.customer.addressbook_set.create(street1='123 Main St', city='New York', state='NY', postal_code='12345', country='US')       
        import datetime
        for product in Product.objects.all():
            price, expire_days = self.getTerms(product)
            if price is None:
                continue
            order = Order.objects.create(contact=self.customer, shipping_cost=0)
            order.orderitem_set.create(
                product=product, 
                quantity=1,
                unit_price=price,
                line_item_price=price,
                expire_date=datetime.datetime.now() + datetime.timedelta(days=expire_days),
                completed=True
            )
            order.recalculate_total()
            order.payments.create(order=order, payment='DUMMY', amount=order.total)
            order.save()
        
    def testProductType(self):
        product1 = Product.objects.get(slug='membership-p1')
        product2 = Product.objects.get(slug='membership-p2')
        self.assertEqual(product1.subscriptionproduct.expire_days, 21)
        self.assertEqual(product1.subscriptionproduct.recurring, True)
        self.assertEqual(product1.subscriptionproduct.recurring, True)
        self.assertEqual(product1.price_set.all()[0].price, Decimal('3.95'))
        self.assertEqual(product2.subscriptionproduct.get_trial_terms(0).expire_days, 7)

    def testCheckout(self):
       pass 
        
    def testCronRebill(self):
        for order in OrderItem.objects.all():
            price, expire_days = self.getTerms(order.product)
            if price is None:
                continue
            self.assertEqual(order.expire_date, datetime.date.today() + datetime.timedelta(days=expire_days))
            #set expire date to today for upcoming cron test
            order.expire_date = datetime.date.today()
            order.save()

        order_count = OrderItem.objects.count()
        self.c = Client()
        self.response = self.c.get(prefix+'/checkout/cron/')
        self.assertEqual(self.response.status_code, 200)
        self.assertEqual(self.response.content, 'Authentication Key Required')
        from django.conf import settings
        self.response = self.c.get(prefix+'/checkout/cron/', data={'key': config_value('PAYMENT','CRON_KEY')})
        self.assertEqual(self.response.status_code, 200)
        self.assertEqual(self.response.content, '')
        self.assert_(order_count < OrderItem.objects.count())
        self.assertEqual(order_count, OrderItem.objects.count()/2)
        for order in OrderItem.objects.filter(expire_date__gt=datetime.datetime.now()):
            price, expire_days = self.getTerms(order.product, ignore_trial=True)
            if price is None:
                continue
            self.assertEqual(order.expire_date, datetime.date.today() + datetime.timedelta(days=expire_days))
            self.assertEqual(order.order.balance, Decimal('0.00'))
        
    def getTerms(self, object, ignore_trial=False):
        if object.subscriptionproduct.get_trial_terms().count() and ignore_trial is False:
            price = object.subscriptionproduct.get_trial_terms(0).price
            expire_days = object.subscriptionproduct.get_trial_terms(0).expire_days
            return price, expire_days
        elif object.is_subscription or ignore_trial is True:
            price = object.price_set.all()[0].price
            expire_days = object.subscriptionproduct.expire_days
            return price, expire_days
        else:
            return None, None #it's not a recurring object so no test will be done

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
#         self.charset = config_value('PAYMENT_PAYMENT_GIFTCERTIFICATE', 'CHARSET')
#         self.format = config_value('PAYMENT_PAYMENT_GIFTCERTIFICATE', 'FORMAT')
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

