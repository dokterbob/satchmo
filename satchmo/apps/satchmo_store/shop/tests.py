from decimal import Decimal
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.core import mail
from django.core.urlresolvers import reverse as url
from django.test import TestCase
from django.test.client import Client
from django.utils.encoding import smart_str
from keyedcache import cache_delete
from l10n.models import Country
from l10n.utils import moneyfmt
from livesettings import config_get
from payment import active_gateways
from product.models import Product
from product.utils import rebuild_pricing, find_auto_discounts
from satchmo_store.contact import CUSTOMER_ID
from satchmo_store.contact.models import *
from satchmo_store.shop import get_satchmo_setting, signals
from satchmo_store.shop.exceptions import CartAddProhibited
from satchmo_store.shop.models import *
from satchmo_utils.templatetags import get_filter_args

import keyedcache

domain = 'http://example.com'
prefix = get_satchmo_setting('SHOP_BASE')
if prefix == '/':
    prefix = ''

def get_step1_post_data(US):
    return {
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
        'copy_address' : True
        }

def make_order_payment(order, paytype=None, amount=None):
    if not paytype:
        paytype = active_gateways()[0][0]

    if not amount:
        amount = order.balance

    pmt = OrderPayment(order=order, payment=paytype.upper(), amount=amount)
    pmt.save()
    return pmt

class ShopTest(TestCase):
    fixtures = ['l10n-data.yaml', 'sample-store-data.yaml', 'products.yaml', 'test-config.yaml', 'initial_data.yaml']

    def setUp(self):
        # Every test needs a client
        cache_delete()
        self.client = Client()
        self.US = Country.objects.get(iso2_code__iexact = "US")
        rebuild_pricing()

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

    def test_cart_adding_errors_nonexistent(self):
        """
        Test proper error reporting when attempting to add items to the cart.
        """

        # Attempting to add a nonexistent product should result in a 404 error.
        response = self.client.post(prefix + '/cart/add/',
            {'productname': 'nonexistent-product', 'quantity': '1'})
        self.assertContains(response, "The product you have requested does not exist.", count=1, status_code=404)

    def test_cart_adding_errors_inactive(self):
        # You should not be able to add a product that is inactive.
        py_shirt = Product.objects.get(slug='PY-Rocks')
        py_shirt.active = False
        py_shirt.save()
        response = self.client.post(prefix + '/cart/add/',
            {'productname': 'PY-Rocks', 'quantity': '1'})
        self.assertContains(response, "That product is not available at the moment.", count=1, status_code=404)

    def test_cart_adding_errors_invalid_qty(self):
        # You should not be able to add a product with a non-valid decimal quantity.
        response = self.client.post(prefix + '/cart/add/',
            {'productname': 'neat-book', '3': 'soft', 'quantity': '1.5a'})

        err = self.client.session.get('ERRORS')
        url = prefix + '/product/neat-book-soft/'
        self.assertRedirects(response, url, status_code=302, target_status_code=200)
        self.assertEqual(err, "Invalid quantity.")

    def test_cart_adding_errors_less_zero(self):
        # You should not be able to add a product with a quantity less than zero.
        response = self.client.post(prefix + '/cart/add/',
            {'productname': 'neat-book', '3': 'soft', 'quantity': '0'})

        err = self.client.session.get('ERRORS')
        url = prefix + '/product/neat-book-soft/'
        self.assertRedirects(response, url, status_code=302, target_status_code=200)
        self.assertEqual(err, "Please enter a positive number.")

    def test_cart_adding_errors_out_of_stock(self):
        # If no_stock_checkout is False, you should not be able to order a
        # product that is out of stock.
        setting = config_get('PRODUCT','NO_STOCK_CHECKOUT')
        setting.update(False)
        response = self.client.post(prefix + '/cart/add/',
            {'productname': 'neat-book', '3': 'soft', 'quantity': '1'})

        err = self.client.session.get('ERRORS')
        url = prefix + '/product/neat-book-soft/'
        self.assertRedirects(response, url, status_code=302, target_status_code=200)
        self.assertEqual(err, "'A really neat book (Soft cover)' is out of stock.")

    def test_product(self):
        # Test for an easily missed reversion. When you lookup a productvariation product then
        # you should get the page of the parent configurableproduct, but with the options for
        # that variation already selected
        response = self.client.get(prefix+'/product/neat-book-soft/')
        self.assertContains(response, 'option value="soft" selected="selected"')
        amount = moneyfmt(Decimal('5.00'))
        self.assertContains(response, smart_str(amount))

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
                                                      "quantity" : '1'})
        content = response.content.split(',')
        self.assertEquals(content[0], '["dj-rocks-s-b"')
        self.assert_(content[1].endswith('20.00"]'))

        # This tests the option price_change feature, and again the productname
        response = self.client.post(prefix+'/product/dj-rocks/prices/', {"1" : "L",
                                                      "2" : "BL",
                                                      "quantity" : '2'})
        content = response.content.split(',')
        self.assertEqual(content[0], '["dj-rocks-l-bl"')
        self.assert_(content[1].endswith('23.00"]'))

    def test_cart_removing(self):
        """
        Validate we can remove an item
        """
        setting = config_get('PRODUCT','NO_STOCK_CHECKOUT')
        setting.update(True)

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
        tax.update('tax.modules.percent')
        pcnt = config_get('TAX', 'PERCENT')
        pcnt.update('10')
        shp = config_get('TAX', 'TAX_SHIPPING')
        shp.update(False)

        self.test_cart_adding()
        response = self.client.post(url('satchmo_checkout-step1'), get_step1_post_data(self.US))
        self.assertRedirects(response, url('DUMMY_satchmo_checkout-step2'),
            status_code=302, target_status_code=200)
        data = {
            'credit_type': 'Visa',
            'credit_number': '4485079141095836',
            'month_expires': '1',
            'year_expires': '2014',
            'ccv': '552',
            'shipping': 'FlatRate'}
        response = self.client.post(url('DUMMY_satchmo_checkout-step2'), data)
        self.assertRedirects(response, url('DUMMY_satchmo_checkout-step3'),
            status_code=302, target_status_code=200)
        response = self.client.get(url('DUMMY_satchmo_checkout-step3'))
        amount = smart_str('Shipping + ' + moneyfmt(Decimal('4.00')))
        self.assertContains(response, amount, count=1, status_code=200)

        amount = smart_str('Tax + ' + moneyfmt(Decimal('4.60')))
        self.assertContains(response, amount, count=1, status_code=200)

        amount = smart_str('Total = ' + moneyfmt(Decimal('54.60')))
        self.assertContains(response, amount, count=1, status_code=200)

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
        response = self.client.post(prefix + '/checkout/', get_step1_post_data(self.US))
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
            'country': self.US.pk,
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
        response = self.client.post(prefix + '/checkout/', get_step1_post_data(self.US))
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
        self.client.post(prefix + '/checkout/', get_step1_post_data(self.US))
        self.assert_(self.client.session.get(CUSTOMER_ID) is not None)
        response = self.client.get('/accounts/logout/?next=%s' % (prefix+'/checkout/'))
        self.assertRedirects(response, prefix + '/checkout/',
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
        self.assertContains(response, "Django Rocks shirt", count=10)
        self.assertContains(response, "Python Rocks shirt", count=1)

class AdminTest(TestCase):
    fixtures = ['l10n-data.yaml', 'sample-store-data.yaml', 'products.yaml', 'initial_data.yaml']

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
        response = self.client.get('/admin/configurable/configurableproduct/1/')
        self.assertContains(response, "Small, Black", status_code=200)

    #def test_productimage_list(self):
        # response = self.client.get('/admin/product/productimage/')
        # self.assertContains(response, "Photo Not Available", status_code=200)

    #def test_productimage(self):
        # response = self.client.get('/admin/product/productimage/1/')
        # self.assertContains(response, "Photo Not Available", status_code=200)

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
        rebuild_pricing()

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

class DiscountAmountTest(TestCase):
    fixtures = ['l10n-data.yaml', 'test_discount.yaml', 'initial_data.yaml']

    def setUp(self):
        self.US = Country.objects.get(iso2_code__iexact = 'US')
        self.site = Site.objects.get_current()
        tax = config_get('TAX','MODULE')
        tax.update('tax.modules.no')
        c = Contact(first_name="Jim", last_name="Tester",
            role=ContactRole.objects.get(pk='Customer'), email="Jim@JimWorld.com")
        c.save()
        ad = AddressBook(contact=c, description="home",
            street1 = "test", state="OR", city="Portland",
            country = self.US, is_default_shipping=True,
            is_default_billing=True)
        ad.save()
        o = Order(contact=c, shipping_cost=Decimal('6.00'), site=self.site)
        o.save()
        small = Order(contact=c, shipping_cost=Decimal('6.00'), site=self.site)
        small.save()

        p = Product.objects.get(slug='neat-book-soft')
        price = p.unit_price
        item1 = OrderItem(order=o, product=p, quantity='1',
            unit_price=price, line_item_price=price)
        item1.save()

        item1s = OrderItem(order=small, product=p, quantity='1',
            unit_price=price, line_item_price=price)
        item1s.save()

        p = Product.objects.get(slug='neat-book-hard')
        price = p.unit_price
        item2 = OrderItem(order=o, product=p, quantity='1',
            unit_price=price, line_item_price=price)
        item2.save()
        self.order = o
        self.small = small

        rebuild_pricing()

    def tearDown(self):
        cache_delete()

    def testBase(self):
        """Check base prices"""
        self.order.recalculate_total(save=False)
        price = self.order.total
        shipcost = self.order.shipping_cost
        shiptotal = self.order.shipping_sub_total
        sub_total = self.order.sub_total
        discount = self.order.discount

        self.assertEqual(price, Decimal('17.00'))
        self.assertEqual(sub_total, Decimal('11.00'))
        self.assertEqual(shipcost, Decimal('6.00'))
        self.assertEqual(shiptotal, Decimal('6.00'))
        self.assertEqual(discount, Decimal('0.00'))

        self.small.recalculate_total(save=False)
        price = self.small.total
        shipcost = self.small.shipping_cost
        shiptotal = self.small.shipping_sub_total
        sub_total = self.small.sub_total
        discount = self.small.discount

        self.assertEqual(price, Decimal('12.00'))
        self.assertEqual(sub_total, Decimal('6.00'))
        self.assertEqual(shipcost, Decimal('6.00'))
        self.assertEqual(shiptotal, Decimal('6.00'))
        self.assertEqual(discount, Decimal('0.00'))


    def testApplyAmountSimple(self):
        """Check straight amount discount."""
        self.order.discount_code="test10"
        self.order.recalculate_total(save=False)
        sub_total = self.order.sub_total
        price = self.order.total
        shipcost = self.order.shipping_cost
        shiptotal = self.order.shipping_sub_total
        discount = self.order.discount

        self.assertEqual(sub_total, Decimal('11.00'))
        self.assertEqual(price, Decimal('7.00'))
        self.assertEqual(shipcost, Decimal('6.00'))
        self.assertEqual(shiptotal, Decimal('6.00'))
        self.assertEqual(discount, Decimal('10.00'))


    def testApplySmallAmountSimple(self):
        """Check small straight amount discount."""
        self.small.discount_code="test10"
        self.small.recalculate_total(save=False)
        sub_total = self.small.sub_total
        price = self.small.total
        shipcost = self.small.shipping_cost
        shiptotal = self.small.shipping_sub_total
        discount = self.small.discount

        self.assertEqual(sub_total, Decimal('6.00'))
        self.assertEqual(price, Decimal('6.00'))
        self.assertEqual(shipcost, Decimal('6.00'))
        self.assertEqual(shiptotal, Decimal('6.00'))
        self.assertEqual(discount, Decimal('6.00'))

    def testApplyAmountShip(self):
        """Check amount discount w/ship."""
        self.order.discount_code="test10ship"
        self.order.recalculate_total(save=False)
        sub_total = self.order.sub_total
        price = self.order.total
        shipcost = self.order.shipping_cost
        shiptotal = self.order.shipping_sub_total
        discount = self.order.discount

        self.assertEqual(sub_total, Decimal('11.00'))
        self.assertEqual(price, Decimal('7.00'))
        self.assertEqual(shipcost, Decimal('6.00'))
        self.assertEqual(shiptotal, Decimal('2.67'))
        self.assertEqual(discount, Decimal('10.00'))

    def testApplySmallAmountShip(self):
        """Check small amount discount w/ship."""
        self.small.discount_code="test10ship"
        self.small.recalculate_total(save=False)
        sub_total = self.small.sub_total
        price = self.small.total
        shipcost = self.small.shipping_cost
        shiptotal = self.small.shipping_sub_total
        discount = self.small.discount

        self.assertEqual(sub_total, Decimal('6.00'))
        self.assertEqual(price, Decimal('2.00'))
        self.assertEqual(shipcost, Decimal('6.00'))
        self.assertEqual(shiptotal, Decimal('1.00'))
        self.assertEqual(discount, Decimal('10.00'))

    def testApplyAmountFreeShip(self):
        """Check amount discount w/free ship."""
        self.order.discount_code="test10freeship"
        self.order.recalculate_total(save=True)
        sub_total = self.order.sub_total
        price = self.order.total
        shipcost = self.order.shipping_cost
        shiptotal = self.order.shipping_sub_total
        discount = self.order.discount
        ship_discount = self.order.shipping_discount

        self.assertEqual(sub_total, Decimal('11.00'))
        self.assertEqual(price, Decimal('1.00'))
        self.assertEqual(shipcost, Decimal('6.00'))
        self.assertEqual(shiptotal, Decimal('0.00'))
        self.assertEqual(ship_discount, Decimal('6.00'))
        self.assertEqual(discount, Decimal('16.00'))

    def testApplySmallAmountFreeShip(self):
        """Check amount discount w/free ship."""
        self.small.discount_code="test10freeship"
        self.small.recalculate_total(save=True)
        sub_total = self.small.sub_total
        price = self.small.total
        shipcost = self.small.shipping_cost
        shiptotal = self.small.shipping_sub_total
        discount = self.small.discount

        self.assertEqual(sub_total, Decimal('6.00'))
        self.assertEqual(price, Decimal('0.00'))
        self.assertEqual(shipcost, Decimal('6.00'))
        self.assertEqual(price, Decimal('0.00'))
        self.assertEqual(shiptotal, Decimal('0.00'))
        self.assertEqual(discount, Decimal('12.00'))


    def testApplyPercentSimple(self):
        self.order.discount_code="test20"
        self.order.recalculate_total(save=False)
        sub_total = self.order.sub_total
        price = self.order.total
        shipcost = self.order.shipping_cost
        shiptotal = self.order.shipping_sub_total
        discount = self.order.discount

        self.assertEqual(sub_total, Decimal('11.00'))
        self.assertEqual(price, Decimal('14.80'))
        self.assertEqual(shipcost, Decimal('6.00'))
        self.assertEqual(shiptotal, Decimal('6.00'))
        self.assertEqual(discount, Decimal('2.20'))

    def testApplySmallPercentSimple(self):
        self.small.discount_code="test20"
        self.small.recalculate_total(save=False)
        sub_total = self.small.sub_total
        price = self.small.total
        shipcost = self.small.shipping_cost
        shiptotal = self.small.shipping_sub_total
        discount = self.small.discount

        self.assertEqual(sub_total, Decimal('6.00'))
        self.assertEqual(price, Decimal('10.80'))
        self.assertEqual(shipcost, Decimal('6.00'))
        self.assertEqual(shiptotal, Decimal('6.00'))
        self.assertEqual(discount, Decimal('1.20'))

    def testApplyPercentShip(self):
        self.order.discount_code="test20ship"
        self.order.recalculate_total(save=False)
        sub_total = self.order.sub_total
        price = self.order.total
        shipcost = self.order.shipping_cost
        shiptotal = self.order.shipping_sub_total
        discount = self.order.discount

        self.assertEqual(sub_total, Decimal('11.00'))
        self.assertEqual(price, Decimal('13.60'))
        self.assertEqual(shipcost, Decimal('6.00'))
        self.assertEqual(shiptotal, Decimal('4.80'))
        self.assertEqual(discount, Decimal('3.40'))

    def testApplySmallPercentShip(self):
        self.small.discount_code="test20ship"
        self.small.recalculate_total(save=False)
        sub_total = self.small.sub_total
        price = self.small.total
        shipcost = self.small.shipping_cost
        shiptotal = self.small.shipping_sub_total
        discount = self.small.discount

        self.assertEqual(sub_total, Decimal('6.00'))
        self.assertEqual(price, Decimal('9.60'))
        self.assertEqual(shipcost, Decimal('6.00'))
        self.assertEqual(shiptotal, Decimal('4.80'))
        self.assertEqual(discount, Decimal('2.40'))

    def testApplySmallPercentFreeShip(self):
        self.small.discount_code="test20freeship"
        self.small.recalculate_total(save=False)
        sub_total = self.small.sub_total
        price = self.small.total
        shipcost = self.small.shipping_cost
        shiptotal = self.small.shipping_sub_total
        discount = self.small.discount

        self.assertEqual(sub_total, Decimal('6.00'))
        self.assertEqual(price, Decimal('4.80'))
        self.assertEqual(shipcost, Decimal('6.00'))
        self.assertEqual(shiptotal, Decimal('0.00'))
        self.assertEqual(discount, Decimal('7.20'))

    def testApplyPercentProducts(self):
        """
        Check that a percentage discount applies only to products specified in
        valid_products.
        """
        #
        # The discount "test10-product" applies only to 'neat-book-soft'.
        #
        # +-----------------+-----------+----------------------+
        # | Product         | Price ($) | Discounted price ($) |
        # +=================+===========+======================+
        # | 'neat-book-hard'|     $5    |      $5              |
        # +-----------------+-----------+----------------------+
        # | 'neat-book-soft'|     $6    |      $5.40           |
        # +-----------------+-----------+----------------------+
        # |          Total: |    $11    |     $10.40           |
        # +-----------------+-----------+----------------------+
        #

        discount_obj = Discount.objects.by_code("test10-product")
        products = {}
        for orderitem in self.order.orderitem_set.all():
            products[orderitem.product.slug] = orderitem.product
        self.assertFalse(discount_obj.valid_for_product(products['neat-book-hard']))
        self.assertTrue(discount_obj.valid_for_product(products['neat-book-soft']))

        self.order.discount_code=discount_obj.code
        self.order.recalculate_total(save=False)
        sub_total = self.order.sub_total
        price = self.order.total
        shipcost = self.order.shipping_cost
        shiptotal = self.order.shipping_sub_total
        discount = self.order.discount

        self.assertEqual(sub_total, Decimal('11.00'))
        self.assertEqual(price, Decimal('16.40'))
        self.assertEqual(shipcost, Decimal('6.00'))
        self.assertEqual(shiptotal, Decimal('6.00'))
        self.assertEqual(discount, Decimal('0.60'))

    def testRetrieveAutoDiscounts(self):
        products = [i.product for i in self.order.orderitem_set.all()]
        discounts = find_auto_discounts(products)

        self.assertEqual(
            set([d.code for d in discounts]),
            set(['test20-auto', 'test20-auto-all']))
        self.assertEqual(
            [d.percentage for d in discounts],
            [Decimal('20.0'), Decimal('20.0')])

    def make_order_payment(order, paytype=None, amount=None):
        if not paytype:
            paytype = active_gateways()[0][0]

        if not amount:
            amount = order.balance

        pmt = OrderPayment(order=order, payment=paytype.upper(), amount=amount)
        pmt.save()
        return pmt

def make_test_order(country, state, include_non_taxed=False, site=None, price=None, quantity=5):
    if not site:
        site = Site.objects.get_current()
    c = Contact(first_name="Tax", last_name="Tester",
        role=ContactRole.objects.get(pk='Customer'), email="tax@example.com")
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
    if not price:
        price = p.unit_price
    item1 = OrderItem(order=o, product=p, quantity=quantity,
        unit_price=price, line_item_price=price*quantity)
    item1.save()

    if include_non_taxed:
        p = Product.objects.get(slug='neat-book-hard')
        price = p.unit_price
        item2 = OrderItem(order=o, product=p, quantity='1',
            unit_price=price, line_item_price=price)
        item2.save()

    return o

class OrderTest(TestCase):
    fixtures = ['l10n-data.yaml', 'test_multishop.yaml', 'products.yaml', 'initial_data.yaml']

    def setUp(self):
        keyedcache.cache_delete()
        self.US = Country.objects.get(iso2_code__iexact='US')

    def tearDown(self):
        cache_delete()

    def testBalanceMethods(self):
        order = make_test_order(self.US, '', include_non_taxed=True)
        order.recalculate_total(save=False)
        price = order.total
        subtotal = order.sub_total

        self.assertEqual(subtotal, Decimal('105.00'))
        self.assertEqual(price, Decimal('115.00'))
        self.assertEqual(order.balance, price)

        paytype = active_gateways()[0][0].upper()

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
        order = make_test_order(self.US, '', include_non_taxed=True)
        order.recalculate_total(save=False)
        price = order.total
        subtotal = order.sub_total

        paytype = active_gateways()[0][0].upper()
        pmt = OrderPayment(order = order, payment=paytype, amount=Decimal("0.000001"))
        pmt.save()

        self.assert_(order.is_partially_paid)

class QuickOrderTest(TestCase):
    """Test quickorder sheet."""
    fixtures = ['l10n-data.yaml', 'sample-store-data.yaml', 'products.yaml', 'test-config.yaml', 'initial_data.yaml']

    def setUp(self):
        keyedcache.cache_delete()
        self.US = Country.objects.get(iso2_code__iexact='US')

    def tearDown(self):
        cache_delete()

    def testQuickOrderAdd(self):
        """Test adding multiple products at once to cart."""
        response = self.client.get(url('satchmo_quick_order'))
        self.assertContains(response, "Django Rocks shirt (Large/Black)", status_code=200)
        self.assertContains(response, "Python Rocks shirt", status_code=200)
        response = self.client.post(url('satchmo_quick_order'), {
            "qty__dj-rocks-l-b" : "2",
            "qty__PY-Rocks" : "1",
        })
        #print response
        self.assertRedirects(response, url('satchmo_cart'),
            status_code=302, target_status_code=200)
        response = self.client.get(prefix+'/cart/')
        self.assertContains(response, "Django Rocks shirt (Large/Black)" , status_code=200)
        self.assertContains(response, "Python Rocks shirt")
        cart = Cart.objects.latest('id')
        self.assertEqual(cart.numItems, 3)
        products = [(item.product.slug, item.quantity) for item in cart.cartitem_set.all()]
        products.sort()
        self.assertEqual(len(products), 2)
        self.assertEqual(products[0][0], 'PY-Rocks')
        self.assertEqual(products[0][1], Decimal(1))
        self.assertEqual(products[1][0], 'dj-rocks-l-b')
        self.assertEqual(products[1][1], Decimal(2))

def vetoAllListener(sender, vetoes={}, **kwargs):
    raise CartAddProhibited(None, "No")

class SignalTest(TestCase):
    fixtures = ['l10n-data.yaml', 'test_multishop.yaml', 'products.yaml']

    def setUp(self):
        keyedcache.cache_delete()
        signals.satchmo_cart_add_verify.connect(vetoAllListener)
        self.US = Country.objects.get(iso2_code__iexact='US')

    def tearDown(self):
        cache_delete()
        signals.satchmo_cart_add_verify.disconnect(vetoAllListener)

    def testCartAddVerifyVeto(self):
        """Test that vetoes from `signals.satchmo_cart_add_verify` are caught and cause an error."""
        try:
            site = Site.objects.get_current()
            cart = Cart(site=site)
            cart.save()
            p = Product.objects.get(slug='dj-rocks-s-b')
            cart.add_item(p, 1)
            order = make_test_order(self.US, '', include_non_taxed=True)
            self.fail('Should have thrown a CartAddProhibited error')

        except CartAddProhibited, cap:
            pass

        self.assertEqual(len(cart), 0)


if __name__ == "__main__":
    import doctest
    doctest.testmod()
