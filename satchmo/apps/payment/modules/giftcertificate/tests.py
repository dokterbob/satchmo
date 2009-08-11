# -*- coding: UTF-8 -*-
from decimal import Decimal
from django.contrib.sites.models import Site
from django.test import TestCase
from keyedcache import cache_delete
from l10n.models import Country
from livesettings import config_get_group, config_value
from models import *
from product.models import Product
from satchmo_store.contact.models import AddressBook, Contact, ContactRole
from satchmo_store.shop.models import Order, OrderItem, OrderItemDetail
from utils import generate_certificate_code, generate_code
import datetime, logging

log = logging.getLogger('giftcertificate.tests')

alphabet = 'abcdefghijklmnopqrstuvwxyz'

def make_test_order(country, state):
    c = Contact(first_name="Gift", last_name="Tester", 
        role=ContactRole.objects.get(pk='Customer'), email="gift@example.com")
    c.save()
    if not isinstance(country, Country):
        country = Country.objects.get(iso2_code__iexact = country)
    ad = AddressBook(contact=c, description="home",
        street1 = "test", state=state, city="Portland",
        country = country, is_default_shipping=True,
        is_default_billing=True)
    ad.save()
    site = Site.objects.get_current()
    o = Order(contact=c, shipping_cost=Decimal('0.00'), site=site)
    o.save()

    p = Product.objects.get(slug='GIFT10')
    price = p.unit_price
    log.debug("creating with price: %s", price)
    item1 = OrderItem(order=o, product=p, quantity='2.0',
        unit_price=price, line_item_price=price*2)
    item1.save()

    detl = OrderItemDetail(name = 'email', value='me@example.com', sort_order=0, item=item1)
    detl.save()
    detl = OrderItemDetail(name = 'message', value='hello there', sort_order=0, item=item1)
    detl.save()

    return o

class TestGenerateCode(TestCase):

    def testGetCode(self):
        c = generate_code(alphabet, '^^^^')
        
        self.assertEqual(len(c), 4)
        
        for ch in c:
            self.assert_(ch in alphabet)
            
    def testGetCode2(self):
        c = generate_code(alphabet, '^^^^-^^^^')
        c2 = generate_code(alphabet, '^^^^-^^^^')
        self.assertNotEqual(c,c2)
        
    def testFormat(self):
        c = generate_code(alphabet, '^-^-^-^')
        for i in (0,2,4,6):
            self.assert_(c[i] in alphabet)
        for i in (1,3,5):
            self.assertEqual(c[i], '-')

class TestGenerateCertificateCode(TestCase):
    def setUp(self):
        self.charset = config_value('PAYMENT_GIFTCERTIFICATE', 'CHARSET')
        self.format = config_value('PAYMENT_GIFTCERTIFICATE', 'FORMAT')
        
    def testGetCode(self):
        c = generate_certificate_code()
        self.assertEqual(len(c), len(self.format))

        chars = [x for x in self.format if not x=='^']
        chars.extend(self.charset)
        for ch in c:
            self.assert_(ch in chars)
    
class TestCertCreate(TestCase):
    fixtures = ['l10n-data.yaml','test_shop']
    
    def setUp(self):
        self.site = Site.objects.get_current()
    
    def tearDown(self):
        cache_delete()

    def testCreate(self):
        gc = GiftCertificate(start_balance = '100.00', site=self.site)
        gc.save()
        
        self.assert_(gc.code)
        self.assertEqual(gc.balance, Decimal('100.00'))

    def testUse(self):
        gc = GiftCertificate(start_balance = '100.00', site=self.site)
        gc.save()
        bal = gc.use('10.00')
        self.assertEqual(bal, Decimal('90.00'))
        self.assertEqual(gc.usages.count(), 1)
        
        
class GiftCertOrderTest(TestCase):

    fixtures = ['l10n-data.yaml', 'test_shop.yaml', 'test_giftcertificate.yaml', 'test_giftcertificate_config.yaml']
    
    def tearDown(self):
        cache_delete()

    def testOrderSuccess(self):
        """Test cert creation on order success"""
        cache_delete()
        order = make_test_order('US', '')
        order.order_success()
    
        certs = order.giftcertificates.all()
        self.assertEqual(len(certs), 1)
        c = certs[0]
        self.assertEqual(c.balance, Decimal('20.00'))
        self.assertEqual(c.recipient_email, 'me@example.com')
        self.assertEqual(c.message, 'hello there')
        
