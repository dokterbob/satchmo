r"""
>>> from satchmo.utils import trunc_decimal

# Test trunc_decimal's rounding behavior.
>>> trunc_decimal("0.004", 2)
Decimal("0.00")
>>> trunc_decimal("0.005", 2)
Decimal("0.01")
>>> trunc_decimal("0.009", 2)
Decimal("0.01")
"""

try:
    from decimal import Decimal
except:
    from django.utils._decimal import Decimal

from django.conf import settings
from django.contrib.auth.models import User
from django.core import mail
from django.core.urlresolvers import reverse as url
from django.test import TestCase
from django.test.client import Client
from django.utils.encoding import smart_str

from django.contrib.sites.models import Site
from satchmo import caching
from satchmo.caching import cache_delete
from satchmo.configuration import config_get, config_value
from satchmo.contact import CUSTOMER_ID
from satchmo.contact.models import Contact, AddressBook
from satchmo.l10n.models import Country
from satchmo.product.models import Product
from satchmo.shop import get_satchmo_setting
from satchmo.shop.models import *
from satchmo.shop.templatetags import get_filter_args

import datetime

domain = 'http://example.com'
prefix = get_satchmo_setting('SHOP_BASE')
if prefix == '/':
    prefix = ''

US = Country.objects.get(iso2_code__iexact = "US")

checkout_step1_post_data = {
    'email': 'sometester@example.com',
    'first_name': 'Teddy',
    'last_name' : 'Tester',
    'phone': '456-123-5555',
    'street1': '8299 Some Street',
    'city': 'Springfield',
    'state': 'MO',
    'postal_code': '81122',
    'country': US.pk,
    'ship_street1': '1011 Some Other Street',
    'ship_city': 'Springfield',
    'ship_state': 'MO',
    'ship_postal_code': '81123',
    'paymentmethod': 'PAYMENT_DUMMY',
    'copy_address' : True}

class ShopTest(TestCase):
    fixtures = ['l10n-data.yaml', 'sample-store-data.yaml', 'products.yaml', 'test-config.yaml']

    def setUp(self):
        # Every test needs a client
        self.client = Client()
        
    def tearDown(self):
        cache_delete()

    def test_main_page(self):
        """
        Look at the main page
        """
        response = self.client.get(prefix+'/')

        # Check that the rendered context contains 4 products
        self.assertContains(response, '<div class = "productImage">',
                            count=4, status_code=200)

    def test_contact_form(self):
        """
        Validate the contact form works
        """

        response = self.client.get(prefix+'/contact/')
        self.assertContains(response, '<h3>Contact Information</h3>',
                            count=1, status_code=200)
        response = self.client.post(prefix+'/contact/', {'name': 'Test Runner',
                              'sender': 'Someone@testrunner.com',
                              'subject': 'A question to test',
                              'inquiry': 'General Question',
                              'contents': 'A lot of info goes here.'})
        self.assertRedirects(response, prefix + '/contact/thankyou/',
            status_code=302, target_status_code=200)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'A question to test')

    def test_new_account(self):
        """
        Validate account creation process
        """
        shop_config = Config.objects.get_current()
        subject = u"Welcome to %s" % shop_config.store_name
        response = self.client.get('/accounts/register/')
        self.assertContains(response, "Please Enter Your Account Information",
                            count=1, status_code=200)
        response = self.client.post('/accounts/register/', {'email': 'someone@test.com',
                                    'first_name': 'Paul',
                                    'last_name' : 'Test',
                                    'password1' : 'pass1',
                                    'password2' : 'pass1',
                                    'newsletter': '0'})
        self.assertRedirects(response, '/accounts/register/complete/',
            status_code=302, target_status_code=200)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, subject)

        response = self.client.get('/accounts/')
        self.assertContains(response, "Welcome, Paul Test.", count=1, status_code=200)
        response = self.client.get('/accounts/logout/')

    def test_cart_adding(self, retest=False):
        """
        Validate we can add some items to the cart
        """
        response = self.client.get(prefix+'/product/dj-rocks/')
        if not retest:
            self.assertContains(response, "Django Rocks shirt", count=2, status_code=200)
        response = self.client.post(prefix+'/cart/add/', { "productname" : "dj-rocks",
                                                      "1" : "L",
                                                      "2" : "BL",
                                                      "quantity" : 2})
        if not retest:
            self.assertRedirects(response, prefix + '/cart/',
                status_code=302, target_status_code=200)
        response = self.client.get(prefix+'/cart/')
        self.assertContains(response, "Django Rocks shirt (Large/Blue)", count=1, status_code=200)

    def test_cart_adding_errors(self):
        """
        Test proper error reporting when attempting to add items to the cart.
        """

        # Attempting to add a nonexistent product should result in a 404 error.
        response = self.client.post(prefix + '/cart/add/',
            {'productname': 'nonexistent-product', 'quantity': '1'})
        self.assertContains(response, "The product you have requested does not exist.", count=1, status_code=404)

        # You should not be able to add a product that is inactive.
        py_shirt = Product.objects.get(slug='PY-Rocks')
        py_shirt.active = False
        py_shirt.save()
        response = self.client.post(prefix + '/cart/add/',
            {'productname': 'PY-Rocks', 'quantity': '1'})
        self.assertContains(response, "That product is not available at the moment.", count=1, status_code=200)

        # You should not be able to add a product with a non-integer quantity.
        response = self.client.post(prefix + '/cart/add/',
            {'productname': 'neat-book', '3': 'soft', 'quantity': '1.5'})
        self.assertContains(response, "Please enter a whole number.", count=1, status_code=200)

        # You should not be able to add a product with a quantity less than one.
        response = self.client.post(prefix + '/cart/add/',
            {'productname': 'neat-book', '3': 'soft', 'quantity': '0'})
        self.assertContains(response, "Please enter a positive number.", count=1, status_code=200)

        # If no_stock_checkout is False, you should not be able to order a
        # product that is out of stock.
        shop_config = Config.objects.get_current()
        shop_config.no_stock_checkout = False
        shop_config.save()
        response = self.client.post(prefix + '/cart/add/',
            {'productname': 'neat-book', '3': 'soft', 'quantity': '1'})
        self.assertContains(response, "&#39;A really neat book (Soft cover)&#39; is out of stock.", count=1, status_code=200)

    def test_product(self):
        # Test for an easily missed reversion. When you lookup a productvariation product then
        # you should get the page of the parent configurableproduct, but with the options for
        # that variation already selected
        response = self.client.get(prefix+'/product/neat-book-soft/')
        self.assertContains(response, 'option value="soft" selected="selected"')
        self.assertContains(response, smart_str("%s5.00" % config_value('SHOP', 'CURRENCY')))

    def test_orphaned_product(self):
        """
        Get the page of a Product that is not in a Category.
        """
        Product.objects.create(name="Orphaned Product", slug="orphaned-product", site=Site.objects.get_current())
        response = self.client.get(prefix + '/product/orphaned-product/')
        self.assertContains(response, 'Orphaned Product')
        self.assertContains(response, 'Software')

    def test_get_price(self):
        """
        Get the price and productname of a ProductVariation.
        """
        response = self.client.get(prefix+'/product/dj-rocks/')
        self.assertContains(response, "Django Rocks shirt", count=2, status_code=200)

        # this tests the unmolested price from the ConfigurableProduct, and
        # makes sure we get a good productname back for the ProductVariation
        response = self.client.post(prefix+'/product/dj-rocks/prices/', {"1" : "S",
                                                      "2" : "B",
                                                      "quantity" : 1})
        content = response.content.split(',')
        self.assertEquals(content[0], '["dj-rocks-s-b"')
        self.assert_(content[1].endswith('20.00"]'))

        # This tests the option price_change feature, and again the productname
        response = self.client.post(prefix+'/product/dj-rocks/prices/', {"1" : "L",
                                                      "2" : "BL",
                                                      "quantity" : 2})
        content = response.content.split(',')
        self.assertEqual(content[0], '["dj-rocks-l-bl"')
        self.assert_(content[1].endswith('23.00"]'))

    def test_cart_removing(self):
        """
        Validate we can remove an item
        """
        shop_config = Config.objects.get_current()
        shop_config.no_stock_checkout = True
        shop_config.save()
        
        self.test_cart_adding(retest=True)
        response = self.client.post(prefix + '/cart/remove/', {'cartitem': '1'})
        #self.assertRedirects(response, prefix + '/cart/',
        #    status_code=302, target_status_code=200)
        response = self.client.get(prefix+'/cart/')
        self.assertContains(response, "Your cart is empty.", count=1, status_code=200)

    def test_checkout(self):
        """
        Run through a full checkout process
        """
        cache_delete()
        tax = config_get('TAX','MODULE')
        tax.update('satchmo.tax.modules.percent')
        pcnt = config_get('TAX', 'PERCENT')
        pcnt.update('10')
        shp = config_get('TAX', 'TAX_SHIPPING')
        shp.update(False)

        self.test_cart_adding()
        response = self.client.post(url('satchmo_checkout-step1'), checkout_step1_post_data)
        self.assertRedirects(response, url('DUMMY_satchmo_checkout-step2'),
            status_code=302, target_status_code=200)
        data = {
            'credit_type': 'Visa',
            'credit_number': '4485079141095836',
            'month_expires': '1',
            'year_expires': '2009',
            'ccv': '552',
            'shipping': 'FlatRate'}
        response = self.client.post(url('DUMMY_satchmo_checkout-step2'), data)
        self.assertRedirects(response, url('DUMMY_satchmo_checkout-step3'),
            status_code=302, target_status_code=200)
        response = self.client.get(url('DUMMY_satchmo_checkout-step3'))
        self.assertContains(response, smart_str("Shipping + %s4.00" % config_value('SHOP', 'CURRENCY')), count=1, status_code=200)
        self.assertContains(response, smart_str("Tax + %s4.60" % config_value('SHOP', 'CURRENCY')), count=1, status_code=200)
        self.assertContains(response, smart_str("Total = %s54.60" % config_value('SHOP', 'CURRENCY')), count=1, status_code=200)
        response = self.client.post(url('DUMMY_satchmo_checkout-step3'), {'process' : 'True'})
        self.assertRedirects(response, url('DUMMY_satchmo_checkout-success'),
            status_code=302, target_status_code=200)
        self.assertEqual(len(mail.outbox), 1)

        # Log in as a superuser
        user = User.objects.create_user('fredsu', 'fred@root.org', 'passwd')
        user.is_staff = True
        user.is_superuser = True
        user.save()
        self.client.login(username='fredsu', password='passwd')

        # Test pdf generation
        response = self.client.get('/admin/print/invoice/1/')
        self.assertContains(response, 'reportlab', status_code=200)
        response = self.client.get('/admin/print/packingslip/1/')
        self.assertContains(response, 'reportlab', status_code=200)
        response = self.client.get('/admin/print/shippinglabel/1/')
        self.assertContains(response, 'reportlab', status_code=200)

    def test_contact_login(self):
        """Check that when a user logs in, the user's existing Contact will be
        used.
        """
        user = User.objects.create_user('teddy', 'sometester@example.com', 'guz90tyc')
        contact = Contact.objects.create(user=user, first_name="Teddy",
            last_name="Tester")
        self.client.login(username='teddy', password='guz90tyc')
        self.test_cart_adding()
        response = self.client.get(url('satchmo_checkout-step1'))
        self.assertContains(response, "Teddy", status_code=200)

    def test_registration_keeps_contact(self):
        """Check that if a user creates a Contact and later registers,
        the existing Contact will be attached to the User.
        """
        self.test_cart_adding()
        response = self.client.post(prefix + '/checkout/', checkout_step1_post_data)
        self.assert_(self.client.session.get(CUSTOMER_ID) is not None)
        response = self.client.get('/accounts/register/')
        self.assertContains(response, "Teddy", status_code=200)
        origcontact = Contact.objects.get(email="sometester@example.com")
        self.assert_(origcontact)
        data = {
            'email': 'sometester@example.com',
            'first_name': 'Teddy',
            'last_name': 'Tester',
            'password1': 'guz90tyc',
            'password2': 'guz90tyc',
            'newsletter': '0'}
        response = self.client.post('/accounts/register/', data)
        self.assertRedirects(response, '/accounts/register/complete/',
            status_code=302, target_status_code=200)
        user = User.objects.get(email="sometester@example.com")
        contact = user.contact_set.get()
        self.assertEqual(contact, origcontact)

    def test_contact_email_security(self):
        """
        Validate that we can't create a new contact with an existing contact's email address.
        Ticket #233
        """
        self.test_new_account()
        response = self.client.get('/accounts/register/')
        init_data = {
            'email': 'somenewtester@example.com',
            'first_name': 'New',
            'last_name': 'Tester',
            'password1': 'new123pass',
            'password2': 'new123pass',
            'newsletter': '0'}
        response = self.client.post('/accounts/register/', init_data)
        self.assertRedirects(response, '/accounts/register/complete/',
            status_code=302, target_status_code=200)
        response = self.client.get('/accounts/update')
        full_data = {
            'first_name': 'New',
            'last_name': 'Tester',
            'email': 'someone@test.com',
            'phone': '901-881-1230',
            'street1': '8 First Street',
            'city': 'Littleton',
            'state': 'MA',
            'postal_code': '01229',
            'country': US.pk,
            'ship_street1': '11 Easy Street',
            'ship_city': 'Littleton',
            'ship_state': 'MA',
            'ship_postal_code': '01229',
        }
        response = self.client.post('/accounts/update/', full_data)
        self.assertContains(response,"That email address is already in use", status_code=200)
        full_data['email'] = 'somenewtester@example.com'
        response = self.client.post('/accounts/update/', full_data)
        response = self.client.get('/accounts/')
        self.assertContains(response,"Email: somenewtester@example.com")

    def test_contact_attaches_to_user(self):
        """Check that if a User registers and later creates a Contact, the
        Contact will be attached to the existing User.
        """
        user = User.objects.create_user('teddy', 'sometester@example.com', 'guz90tyc')
        self.assertEqual(user.contact_set.count(), 0)
        self.client.login(username='teddy', password='guz90tyc')
        self.test_cart_adding()
        response = self.client.post(prefix + '/checkout/', checkout_step1_post_data)
        self.assertEqual(user.contact_set.count(), 1)

    def test_logout(self):
        """The logout view should remove the user and contact id from the
        session.
        """
        user = User.objects.create_user('teddy', 'sometester@example.com', 'guz90tyc')
        self.client.login(username='teddy', password='guz90tyc')
        response = self.client.get('/accounts/') # test logged in status
        self.assertContains(response, "the user you've logged in as doesn't have any contact information.", status_code=200)
        self.test_cart_adding()
        self.client.post(prefix + '/checkout/', checkout_step1_post_data)
        self.assert_(self.client.session.get(CUSTOMER_ID) is not None)
        response = self.client.get('/accounts/logout/')
        self.assertRedirects(response, prefix + '/',
            status_code=302, target_status_code=200)
        self.assert_(self.client.session.get(CUSTOMER_ID) is None)
        response = self.client.get('/accounts/') # test logged in status
        self.assertRedirects(response, '/accounts/login/?next=/accounts/',
            status_code=302, target_status_code=200)

    def test_search(self):
        """
        Do some basic searches to make sure it all works as expected
        """
        response = self.client.get(prefix+'/search/', {'keywords':'python'})
        self.assertContains(response, "Python Rocks shirt", count=1)
        response = self.client.get(prefix+'/search/', {'keywords':'django+book'})
        self.assertContains(response, "Nothing found")
        response = self.client.get(prefix+'/search/', {'keywords':'shirt'})
        self.assertContains(response, "Shirts", count=2)
        self.assertContains(response, "Short Sleeve", count=2)
        self.assertContains(response, "Django Rocks shirt", count=1)
        self.assertContains(response, "Python Rocks shirt", count=1)

    def test_custom_product(self):
        """
        Verify that the custom product is working as expected.
        """
        pm = config_get("PRODUCT", "PRODUCT_TYPES")
        pm.update(["product::ConfigurableProduct","product::ProductVariation", "product::CustomProduct", "product::SubscriptionProduct"])
        
        response = self.client.get(prefix+"/")
        self.assertContains(response, "Computer", count=1)
        response = self.client.get(prefix+"/product/satchmo-computer/")
        self.assertContains(response, "Memory", count=1)
        self.assertContains(response, "Case", count=1)
        self.assertContains(response, "Monogram", count=1)
        response = self.client.post(prefix+'/cart/add/', { "productname" : "satchmo-computer",
                                                      "5" : "1.5gb",
                                                      "6" : "mid",
                                                      "custom_monogram": "CBM",
                                                      "quantity" : 1})
        self.assertRedirects(response, prefix + '/cart/',
            status_code=302, target_status_code=200)
        response = self.client.get(prefix+'/cart/')
        self.assertContains(response, '/satchmo-computer/">satchmo computer', count=1, status_code=200)
        self.assertContains(response, smart_str("%s168.00" % config_value('SHOP', 'CURRENCY')), count=3)
        self.assertContains(response, smart_str("Monogram: CBM  %s10.00" % config_value('SHOP', 'CURRENCY')), count=1)
        self.assertContains(response, smart_str("Case - External Case: Mid  %s10.00" % config_value('SHOP', 'CURRENCY')), count=1)
        self.assertContains(response, smart_str("Memory - Internal RAM: 1.5 GB  %s25.00" % config_value('SHOP', 'CURRENCY')), count=1)
        response = self.client.post(url('satchmo_checkout-step1'), checkout_step1_post_data)
        self.assertRedirects(response, url('DUMMY_satchmo_checkout-step2'),
            status_code=302, target_status_code=200)
        data = {
            'credit_type': 'Visa',
            'credit_number': '4485079141095836',
            'month_expires': '1',
            'year_expires': '2012',
            'ccv': '552',
            'shipping': 'FlatRate'}
        response = self.client.post(url('DUMMY_satchmo_checkout-step2'), data)
        self.assertRedirects(response, url('DUMMY_satchmo_checkout-step3'),
            status_code=302, target_status_code=200)
        response = self.client.get(url('DUMMY_satchmo_checkout-step3'))
        self.assertContains(response, smart_str("satchmo computer - %s168.00" % config_value('SHOP', 'CURRENCY')), count=1, status_code=200)
        response = self.client.post(url('DUMMY_satchmo_checkout-step3'), {'process' : 'True'})
        self.assertRedirects(response, url('DUMMY_satchmo_checkout-success'),
            status_code=302, target_status_code=200)
        self.assertEqual(len(mail.outbox), 1)

class AdminTest(TestCase):
    fixtures = ['l10n-data.yaml', 'sample-store-data.yaml', 'products.yaml']

    def setUp(self):
        self.client = Client()
        user = User.objects.create_user('fredsu', 'fred@root.org', 'passwd')
        user.is_staff = True
        user.is_superuser = True
        user.save()
        self.client.login(username='fredsu', password='passwd')

    def tearDown(self):
        cache_delete()

    def test_index(self):
        response = self.client.get('/admin/')
        self.assertContains(response, "contact/contact/", status_code=200)

    #def test_product(self):
        response = self.client.get('/admin/product/product/1/')
        self.assertContains(response, "Django Rocks shirt", status_code=200)

    #def test_configurableproduct(self):
        response = self.client.get('/admin/product/configurableproduct/1/')
        self.assertContains(response, "Small, Black", status_code=200)

    #def test_productimage_list(self):
        response = self.client.get('/admin/product/productimage/')
        self.assertContains(response, "Photo Not Available", status_code=200)

    #def test_productimage(self):
        response = self.client.get('/admin/product/productimage/1/')
        self.assertContains(response, "Photo Not Available", status_code=200)

class FilterUtilTest(TestCase):
    """Test the templatetags util class"""

    def tearDown(self):
        cache_delete()

    def test_simple_get_args(self):
        args, kwargs = get_filter_args('one=1,two=2')
        self.assertEqual(len(args), 0)

        self.assertEqual(kwargs['one'], '1')

        self.assertEqual(kwargs['two'], '2')

    def test_extended_get_args(self):
        args, kwargs = get_filter_args('test,one=1,two=2')
        self.assertEqual(args[0], 'test')

        self.assertEqual(kwargs['one'], '1')

        self.assertEqual(kwargs['two'], '2')

    def test_numerical_get_args(self):
        args, kwargs = get_filter_args('test,one=1,two=2', (), ('one','two'))
        self.assertEqual(args[0], 'test')

        self.assertEqual(kwargs['one'], 1)

        self.assertEqual(kwargs['two'], 2)

    def test_keystrip_get_args(self):
        args, kwargs = get_filter_args('test,one=1,two=2', ('one'), ('one'))
        self.assertEqual(args[0], 'test')

        self.assertEqual(kwargs['one'], 1)

        self.assertFalse('two' in kwargs)


    def test_stripquotes_get_args(self):
        args, kwargs = get_filter_args('"test",one="test",two=2', stripquotes=True)
        self.assertEqual(args[0], 'test')

        self.assertEqual(kwargs['one'], 'test')

        self.assertEqual(kwargs['two'], '2')

        args, kwargs = get_filter_args('"test",one="test",two=2', stripquotes=False)
        self.assertEqual(args[0], '"test"')

        self.assertEqual(kwargs['one'], '"test"')

class CartTest(TestCase):
    fixtures = ['l10n-data.yaml', 'sample-store-data.yaml', 'products.yaml', 'test-config.yaml']

    def tearDown(self):
        cache_delete()

    def test_line_cost(self):
        p = Product.objects.get(slug__iexact='dj-rocks')
        lb = Product.objects.get(slug__iexact='dj-rocks-l-bl')
        sb = Product.objects.get(slug__iexact='dj-rocks-s-b')

        cart = Cart(site=Site.objects.get_current())
        cart.save()
        cart.add_item(sb, 1)
        self.assertEqual(cart.numItems, 1)
        self.assertEqual(cart.total, Decimal("20.00"))

        cart.add_item(lb, 1)
        self.assertEqual(cart.numItems, 2)
        items = list(cart.cartitem_set.all())
        item1 = items[0]
        item2 = items[1]
        self.assertEqual(item1.unit_price, Decimal("20.00"))
        self.assertEqual(item2.unit_price, Decimal("23.00"))
        self.assertEqual(cart.total, Decimal("43.00"))

class ConfigTest(TestCase):
    fixtures = ['l10n-data.yaml', 'sample-store-data.yaml', 'test-config.yaml']

    def tearDown(self):
        cache_delete()

    def test_base_url(self):
        config = Config.objects.get_current()
        self.assertEquals(config.base_url, domain)

def make_test_order(country, state, include_non_taxed=False, site=None):
    if not site:
        site = Site.objects.get_current()
    c = Contact(first_name="Tax", last_name="Tester", 
        role="Customer", email="tax@example.com")
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
    
    p = Product.objects.get(slug='dj-rocks-s-b')
    price = p.unit_price
    item1 = OrderItem(order=o, product=p, quantity=5,
        unit_price=price, line_item_price=price*5)
    item1.save()
    
    if include_non_taxed:
        p = Product.objects.get(slug='neat-book-hard')
        price = p.unit_price
        item2 = OrderItem(order=o, product=p, quantity=1,
            unit_price=price, line_item_price=price)
        item2.save()
    
    return o

class OrderTest(TestCase):
    fixtures = ['l10n-data.yaml', 'test_multishop.yaml', 'products.yaml']    
    
    def setUp(self):
        caching.cache_delete()

    def tearDown(self):
        cache_delete()

    def testBalanceMethods(self):
        order = make_test_order(US, '', include_non_taxed=True)
        order.recalculate_total(save=False)
        price = order.total
        subtotal = order.sub_total
    
        self.assertEqual(subtotal, Decimal('105.00'))
        self.assertEqual(price, Decimal('115.00'))
        self.assertEqual(order.balance, price)
    
        paytype = config_value('PAYMENT', 'MODULES')[0]
        pmt = OrderPayment(order = order, payment=paytype, amount=Decimal("5.00"))
        pmt.save()
    
        self.assertEqual(order.balance, Decimal("110.00"))
        self.assertEqual(order.balance_paid, Decimal("5.00"))

        self.assert_(order.is_partially_paid)
    
        pmt = OrderPayment(order = order, payment=paytype, amount=Decimal("110.00"))
        pmt.save()
    
        self.assertEqual(order.balance, Decimal("0.00"))
        self.assertEqual(order.is_partially_paid, False)
        self.assert_(order.paid_in_full)

    def testSmallPayment(self):
        order = make_test_order(US, '', include_non_taxed=True)
        order.recalculate_total(save=False)
        price = order.total
        subtotal = order.sub_total
        
        paytype = config_value('PAYMENT', 'MODULES')[0]
        pmt = OrderPayment(order = order, payment=paytype, amount=Decimal("0.000001"))
        pmt.save()
    
        self.assert_(order.is_partially_paid)


if __name__ == "__main__":
    import doctest
    doctest.testmod()
