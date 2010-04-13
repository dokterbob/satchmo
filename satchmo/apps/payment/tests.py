from decimal import Decimal
from django.contrib.sites.models import Site
from django.core import urlresolvers
from django.core.urlresolvers import reverse as url
from django.test import TestCase
from django.test.client import Client
from l10n.models import *
from livesettings import config_get, config_get_group
from payment import utils
from product.models import *
from satchmo_store.contact.models import *
from satchmo_store.shop.models import *
from satchmo_utils.dynamic import lookup_template, lookup_url
from urls import make_urlpatterns
import keyedcache

alphabet = 'abcdefghijklmnopqrstuvwxyz'

def make_test_order(country, state, site=None, orderitems=None):
    if not orderitems:
        orderitems = [('dj-rocks-s-b', 5), ('neat-book-hard', 1)]

    if not site:
        site = Site.objects.get_current()

    c = Contact(first_name="Order", last_name="Tester",
        role=ContactRole.objects.get(pk='Customer'), email="order@example.com")
    c.save()

    if not isinstance(country, Country):
        country = Country.objects.get(iso2_code__iexact = country)

    ad = AddressBook(contact=c, description="home",
        street1 = "test", state=state, city="Portland",
        country = country, is_default_shipping=True,
        is_default_billing=True)
    ad.save()
    o = Order(contact=c, shipping_cost=Decimal('10.00'), site = site)
    o.save()

    for slug, qty in orderitems:
        p = Product.objects.get(slug=slug)
        price = p.unit_price
        item = OrderItem(order=o, product=p, quantity=qty,
            unit_price=price, line_item_price=price*qty)
        item.save()

    return o

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
                                                      "quantity" : '2'})
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
                                                      "quantity" : '10'})
        self.assertRedirects(response, carturl,
            status_code=302, target_status_code=200)
        response = self.client.get(url('satchmo_checkout-step1'))
        self.assertContains(response, "Billing Information", count=1, status_code=200)

class TestPaymentHandling(TestCase):
    fixtures = ['l10n-data.yaml', 'sample-store-data.yaml', 'products.yaml', 'test-config.yaml', 'initial_data.yaml']

    def setUp(self):
        self.client = Client()
        self.US = Country.objects.get(iso2_code__iexact = "US")

    def tearDown(self):
        keyedcache.cache_delete()

    def test_authorize(self):
        """Test making an authorization using DUMMY."""
        order = make_test_order(self.US, '')
        self.assertEqual(order.balance, order.total)
        self.assertEqual(order.total, Decimal('125.00'))

        processor = utils.get_processor_by_key('PAYMENT_DUMMY')
        processor.create_pending_payment(order=order, amount=order.total)

        self.assertEqual(order.pendingpayments.count(), 1)
        self.assertEqual(order.payments.count(), 1)

        pending = order.pendingpayments.all()[0]
        self.assertEqual(pending.amount, order.total)

        payment = order.payments.all()[0]
        self.assertEqual(payment.amount, Decimal('0'))

        self.assertEqual(pending.capture, payment)

        self.assertEqual(order.balance_paid, Decimal('0'))
        self.assertEqual(order.authorized_remaining, Decimal('0'))

        processor.prepare_data(order)
        result = processor.authorize_payment()
        self.assertEqual(result.success, True)
        auth = result.payment
        self.assertEqual(type(auth), OrderAuthorization)

        self.assertEqual(order.authorized_remaining, Decimal('125.00'))

        result = processor.capture_authorized_payment(auth)
        self.assertEqual(result.success, True)
        payment = result.payment
        self.assertEqual(auth.capture, payment)
        order = Order.objects.get(pk=order.id)
        self.assertEqual(order.status, 'New')
        self.assertEqual(order.balance, Decimal('0'))

    def test_authorize_multiple(self):
        """Test making multiple authorization using DUMMY."""
        order = make_test_order(self.US, '')
        self.assertEqual(order.balance, order.total)
        self.assertEqual(order.total, Decimal('125.00'))

        processor = utils.get_processor_by_key('PAYMENT_DUMMY')
        processor.create_pending_payment(order=order, amount=Decimal('25.00'))

        self.assertEqual(order.pendingpayments.count(), 1)
        self.assertEqual(order.payments.count(), 1)

        pending = order.pendingpayments.all()[0]

        self.assertEqual(pending.amount, Decimal('25.00'))
        processor.prepare_data(order)
        result = processor.authorize_payment()
        self.assertEqual(result.success, True)
        #self.assertEqual(order.authorized_remaining, Decimal('25.00'))
        #self.assertEqual(order.balance, Decimal('100.00'))

        processor.create_pending_payment(order=order, amount=Decimal('100.00'))
        result = processor.authorize_payment()

        results = processor.capture_authorized_payments()
        self.assertEqual(len(results), 2)

        r1 = results[0]
        r2 = results[1]
        self.assertEqual(r1.success, True)
        self.assertEqual(r2.success, True)
        order = Order.objects.get(pk=order.id)
        self.assertEqual(order.status, 'New')
        self.assertEqual(order.balance, Decimal('0'))

    def test_capture(self):
        """Test making a capture without authorization using DUMMY."""
        order = make_test_order(self.US, '')
        self.assertEqual(order.balance, order.total)
        self.assertEqual(order.total, Decimal('125.00'))

        processor = utils.get_processor_by_key('PAYMENT_DUMMY')
        processor.create_pending_payment(order=order, amount=order.total)

        processor.prepare_data(order)
        result = processor.capture_payment()
        self.assertEqual(result.success, True)
        pmt1 = result.payment
        self.assertEqual(type(pmt1), OrderPayment)

        self.assertEqual(order.authorized_remaining, Decimal('0.00'))

        self.assertEqual(result.success, True)
        payment = result.payment
        self.assertEqual(pmt1, payment)
        order = Order.objects.get(pk=order.id)
        self.assertEqual(order.status, 'New')
        self.assertEqual(order.balance, Decimal('0'))



    def test_multiple_pending(self):
        """Test that creating a second pending payment deletes the first one."""
        order = make_test_order(self.US, '')
        self.assertEqual(order.balance, order.total)
        self.assertEqual(order.total, Decimal('125.00'))

        processor = utils.get_processor_by_key('PAYMENT_DUMMY')
        pend1 = processor.create_pending_payment(order=order, amount=order.total)
        pend2 = processor.create_pending_payment(order=order, amount=order.total)

        self.assertEqual(order.pendingpayments.count(), 1)
        self.assertEqual(order.payments.count(), 1)
