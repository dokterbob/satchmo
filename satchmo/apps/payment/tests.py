# -*- coding: UTF-8 -*-
from django.conf import settings
from django.contrib.sites.models import Site
from django.core import urlresolvers
from django.core.urlresolvers import reverse as url
from django.test import TestCase
from django.test.client import Client
from django.test.client import Client
import keyedcache
from livesettings import config_get_group, config_value, config_get
from satchmo_store.contact.models import *
from l10n.models import *
from product.models import *
from satchmo_store.shop.models import *
from satchmo_utils.dynamic import lookup_template, lookup_url
from urls import make_urlpatterns

try:
    from decimal import Decimal
except:
    from django.utils._decimal import Decimal

alphabet = 'abcdefghijklmnopqrstuvwxyz'

class TestRecurringBilling(TestCase):
    fixtures = ['l10n-data.yaml', 'test_shop.yaml', 'sub_products', 'config']

    def setUp(self):
        self.customer = Contact.objects.create(first_name='Jane', last_name='Doe')
        US = Country.objects.get(iso2_code__iexact="US")
        self.customer.addressbook_set.create(street1='123 Main St', city='New York', state='NY', postal_code='12345', country=US)       
        import datetime
        site = Site.objects.get_current()
        for product in Product.objects.all():
            price, expire_length = self.getTerms(product)
            if price is None:
                continue
            order = Order.objects.create(contact=self.customer, shipping_cost=0, site=site)
            order.orderitem_set.create(
                product=product, 
                quantity=1,
                unit_price=price,
                line_item_price=price,
                expire_date=datetime.datetime.now() + datetime.timedelta(days=expire_length),
                completed=True
            )
            order.recalculate_total()
            order.payments.create(order=order, payment='DUMMY', amount=order.total)
            order.save()
        
    def tearDown(self):
        keyedcache.cache_delete()
        
    def testProductType(self):
        product1 = Product.objects.get(slug='membership-p1')
        product2 = Product.objects.get(slug='membership-p2')
        self.assertEqual(product1.subscriptionproduct.expire_length, 21)
        self.assertEqual(product1.subscriptionproduct.recurring, True)
        self.assertEqual(product1.subscriptionproduct.recurring, True)
        self.assertEqual(product1.price_set.all()[0].price, Decimal('3.95'))
        self.assertEqual(product2.subscriptionproduct.get_trial_terms(0).expire_length, 7)

    def testCheckout(self):
       pass 
        
    def testCronRebill(self):
        for order in OrderItem.objects.all():
            price, expire_length = self.getTerms(order.product)
            if price is None:
                continue
            self.assertEqual(order.expire_date, datetime.date.today() + datetime.timedelta(days=expire_length))
            #set expire date to today for upcoming cron test
            order.expire_date = datetime.date.today()
            order.save()

        order_count = OrderItem.objects.count()
        self.c = Client()
        url = urlresolvers.reverse('satchmo_cron_rebill')
        self.response = self.c.get(url)
        self.assertEqual(self.response.status_code, 200)
        self.assertEqual(self.response.content, 'Authentication Key Required')
        from django.conf import settings
        self.response = self.c.get(url, data={'key': config_value('PAYMENT','CRON_KEY')})
        self.assertEqual(self.response.status_code, 200)
        self.assertEqual(self.response.content, '')
        self.assert_(order_count < OrderItem.objects.count())
        self.assertEqual(order_count, OrderItem.objects.count()/2.0)
        for order in OrderItem.objects.filter(expire_date__gt=datetime.datetime.now()):
            price, expire_length = self.getTerms(order.product, ignore_trial=True)
            if price is None:
                continue
            self.assertEqual(order.expire_date, datetime.date.today() + datetime.timedelta(days=expire_length))
            self.assertEqual(order.order.balance, Decimal('0.00'))
        
    def getTerms(self, object, ignore_trial=False):
        if object.subscriptionproduct.get_trial_terms().count() and ignore_trial is False:
            price = object.subscriptionproduct.get_trial_terms(0).price
            expire_length = object.subscriptionproduct.get_trial_terms(0).expire_length
            return price, expire_length
        elif object.is_subscription or ignore_trial is True:
            price = object.price_set.all()[0].price
            expire_length = object.subscriptionproduct.expire_length
            return price, expire_length
        else:
            return None, None #it's not a recurring object so no test will be done

class TestModulesSettings(TestCase):

    def setUp(self):
        self.dummy = config_get_group('PAYMENT_DUMMY')

    def tearDown(self):
        keyedcache.cache_delete()

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

class TestMinimumOrder(TestCase):
    fixtures = ['l10n-data.yaml', 'sample-store-data.yaml', 'products.yaml', 'test-config.yaml']

    def setUp(self):
        # Every test needs a client
        self.client = Client()
        
    def tearDown(self):
        keyedcache.cache_delete()

    def test_checkout_minimums(self):
        """
        Validate we can add some items to the cart
        """
        min_order = config_get('PAYMENT', 'MINIMUM_ORDER')
        
        #start with no min.
        min_order.update("0.00")
        producturl = urlresolvers.reverse("satchmo_product", kwargs={'product_slug' : 'dj-rocks'})
        response = self.client.get(producturl)
        self.assertContains(response, "Django Rocks shirt", count=2, status_code=200)
        cartadd = urlresolvers.reverse('satchmo_cart_add')
        response = self.client.post(cartadd, { "productname" : "dj-rocks",
                                                      "1" : "L",
                                                      "2" : "BL",
                                                      "quantity" : 2})
        carturl = urlresolvers.reverse('satchmo_cart')                                              
        self.assertRedirects(response, carturl,
            status_code=302, target_status_code=200)
        response = self.client.get(carturl)
        self.assertContains(response, "Django Rocks shirt (Large/Blue)", count=1, status_code=200)
        response = self.client.get(url('satchmo_checkout-step1'))
        self.assertContains(response, "Billing Information", count=1, status_code=200)

        # now check for min order not met
        min_order.update("100.00")
        response = self.client.get(url('satchmo_checkout-step1'))
        self.assertContains(response, "This store requires a minimum order", count=1, status_code=200)
        
        # add a bunch of shirts, to make the min order
        response = self.client.post(cartadd, { "productname" : "dj-rocks",
                                                      "1" : "L",
                                                      "2" : "BL",
                                                      "quantity" : 10})
        self.assertRedirects(response, carturl,
            status_code=302, target_status_code=200)
        response = self.client.get(url('satchmo_checkout-step1'))
        self.assertContains(response, "Billing Information", count=1, status_code=200)
