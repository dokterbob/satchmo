from django.test import TestCase
from django.test.client import Client
from django.core import mail
from django.core.urlresolvers import reverse as url
from django.conf import settings
from django.contrib.auth.models import User
from django.utils.encoding import smart_str
from satchmo.caching import cache_delete
from satchmo.contact.models import Contact
from satchmo.shop.templatetags import get_filter_args
from satchmo.configuration import config_value, config_get

domain = 'http://testserver'
prefix = settings.SHOP_BASE
if prefix == '/':
    prefix = ''

checkout_step1_post_data = {
    'email': 'sometester@example.com',
    'first_name': 'Teddy',
    'last_name' : 'Tester',
    'phone': '456-123-5555',
    'street1': '8299 Some Street',
    'city': 'Springfield',
    'state': 'MO',
    'postal_code': '81122',
    'country': 'US',
    'ship_street1': '1011 Some Other Street',
    'ship_city': 'Springfield',
    'ship_state': 'MO',
    'ship_postal_code': '81123',
    'paymentmethod': 'DUMMY'}

class ShopTest(TestCase):
    fixtures = ['l10n-data.yaml', 'sample-store-data.yaml', 'products.yaml', 'test-config.yaml']

    def setUp(self):
        # Every test needs a client
        self.client = Client()

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
        self.assertRedirects(response, domain + prefix+'/contact/thankyou/', status_code=302, target_status_code=200)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'A question to test')

    def test_new_account(self):
        """
        Validate account creation process
        """
        from satchmo.shop.models import Config
        shop_config = Config.get_shop_config()
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
        self.assertRedirects(response, domain +'/accounts/register/complete/', status_code=302, target_status_code=200)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, subject)

        response = self.client.get('/accounts/')
        self.assertContains(response, "Welcome, Paul Test.", count=1, status_code=200)
        response = self.client.get('/accounts/logout/')

    def test_cart_adding(self):
        """
        Validate we can add some items to the cart
        """
        response = self.client.get(prefix+'/product/DJ-Rocks/')
        self.assertContains(response, "Django Rocks shirt", count=2, status_code=200)
        response = self.client.post(prefix+'/cart/add/', { "productname" : "DJ-Rocks",
                                                      "1" : "L",
                                                      "2" : "BL",
                                                      "quantity" : 2})
        self.assertRedirects(response, domain + prefix+'/cart/', status_code=302, target_status_code=200)
        response = self.client.get(prefix+'/cart/')
        self.assertContains(response, "Django Rocks shirt (Large/Blue)", count=1, status_code=200)

    def test_product(self):
        # Test for an easily missed reversion. When you lookup a productvariation product then
        # you should get the page of the parent configurableproduct, but with the options for
        # that variation already selected
        response = self.client.get(prefix+'/product/neat-book_soft/')
        self.assertContains(response, 'option value="soft" selected="selected"')
        self.assertContains(response, smart_str("%s5.00" % config_value('SHOP', 'CURRENCY')))

    def test_get_price(self):
        """
        Get a price/productname for a ProductVariation
        """
        response = self.client.get(prefix+'/product/DJ-Rocks/')
        self.assertContains(response, "Django Rocks shirt", count=2, status_code=200)

        # this tests the unmolested price from the ConfigurableProduct, and
        # makes sure we get a good productname back for the ProductVariation
        response = self.client.post(prefix+'/product/DJ-Rocks/prices/', {"1" : "S",
                                                      "2" : "B",
                                                      "quantity" : 1})
        content = response.content.split(',')
        self.assertEquals(content[0], '["DJ-Rocks_S_B"')
        self.assert_(content[1].endswith('20.00"]'))

        # This tests the option price_change feature, and again the productname
        response = self.client.post(prefix+'/product/DJ-Rocks/prices/', {"1" : "L",
                                                      "2" : "BL",
                                                      "quantity" : 2})
        content = response.content.split(',')
        self.assertEqual(content[0], '["DJ-Rocks_L_BL"')
        self.assert_(content[1].endswith('23.00"]'))

#        response = self.client.get(prefix+'/product/neat-software/')
#        self.assertContains(response, "Neat Software", count=1, status_code=200)

        # The following 2 test using the ProductVariation Price
#        response = self.client.post(prefix+'/product/neat-software/prices/', {"4" : "full",
#                                                      "quantity" : 1})
#        self.assertContains(response, "$5.00", count=1, status_code=200)
#        response = self.client.post(prefix+'/product/neat-software/prices/', {"4" : "upgrade",
#                                                      "quantity" : 1})
#        self.assertContains(response, "$1.00", count=1, status_code=200)

        # This tests quantity discounts
#        response = self.client.post(prefix+'/product/neat-software/prices/', {"4" : "full",
#                                                      "quantity" : 50})
#        self.assertContains(response, "$2.00", count=1, status_code=200)

    def test_cart_removing(self):
        """
        Validate we can remove an item
        """
        self.test_cart_adding()
        response = self.client.post(prefix + '/cart/remove/', {'cartitem': '1'})
        self.assertRedirects(response, domain + prefix+'/cart/', status_code=302, target_status_code=200)
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
        self.assertRedirects(response, domain + url('DUMMY_satchmo_checkout-step2'), status_code=302, target_status_code=200)
        data = {
            'credit_type': 'Visa',
            'credit_number': '4485079141095836',
            'month_expires': '1',
            'year_expires': '2009',
            'ccv': '552',
            'shipping': 'FlatRate'}
        response = self.client.post(url('DUMMY_satchmo_checkout-step2'), data)
        self.assertRedirects(response, domain + url('DUMMY_satchmo_checkout-step3'), status_code=302, target_status_code=200)
        response = self.client.get(url('DUMMY_satchmo_checkout-step3'))
        #print response
        self.assertContains(response, smart_str("Shipping + %s4.00" % config_value('SHOP', 'CURRENCY')), count=1, status_code=200)
        self.assertContains(response, smart_str("Tax + %s4.60" % config_value('SHOP', 'CURRENCY')), count=1, status_code=200)
        self.assertContains(response, smart_str("Total = %s54.60" % config_value('SHOP', 'CURRENCY')), count=1, status_code=200)
        response = self.client.post(url('DUMMY_satchmo_checkout-step3'), {'process' : 'True'})
        self.assertRedirects(response, domain + url('DUMMY_satchmo_checkout-success'), status_code=302, target_status_code=200)
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
        self.client.post(prefix + '/checkout/', checkout_step1_post_data)
        response = self.client.get('/accounts/register/')
        self.assertContains(response, "Teddy", status_code=200)
        data = {
            'email': 'sometester@example.com',
            'first_name': 'Teddy',
            'last_name': 'Tester',
            'password1': 'guz90tyc',
            'password2': 'guz90tyc',
            'newsletter': '0'}
        response = self.client.post('/accounts/register/', data)
        self.assertRedirects(response, domain+'/accounts/register/complete/',
            status_code=302, target_status_code=200)
        user = User.objects.get(email="sometester@example.com")
        contact = user.contact_set.get()
        self.assertEqual(contact.billing_address.street1, "8299 Some Street")
        self.assertEqual(contact.shipping_address.street1, "1011 Some Other Street")
        self.assertEqual(contact.primary_phone.phone, "456-123-5555")

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
        self.assertRedirects(response, domain+'/accounts/register/complete/',
            status_code=302, target_status_code=200)
        response = self.client.get('/accounts/update')
        full_data = {
            'email': 'someone@test.com',
            'phone': '901-881-1230',
            'street1': '8 First Street',
            'city': 'Littleton',
            'state': 'MA',
            'postal_code': '01229',
            'country': 'US',
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
        self.client.post(prefix + '/checkout/', checkout_step1_post_data)
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
        self.assert_(self.client.session.get('custID') is not None)
        response = self.client.get('/accounts/logout/')
        self.assertRedirects(response, domain + prefix + '/', status_code=302, target_status_code=200)
        self.assert_(self.client.session.get('custID') is None)
        response = self.client.get('/accounts/') # test logged in status
        self.assertRedirects(response, domain +'/accounts/login/?next=/accounts/', status_code=302, target_status_code=200)

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
        self.assertRedirects(response, domain + prefix+'/cart/', status_code=302, target_status_code=200)
        response = self.client.get(prefix+'/cart/')
        self.assertContains(response, '/satchmo-computer/">satchmo computer', count=1, status_code=200)
        self.assertContains(response, smart_str("%s168.00" % config_value('SHOP', 'CURRENCY')), count=3)
        self.assertContains(response, smart_str("Monogram: CBM  %s10.00" % config_value('SHOP', 'CURRENCY')), count=1)
        self.assertContains(response, smart_str("Case - External Case: Mid  %s10.00" % config_value('SHOP', 'CURRENCY')), count=1)
        self.assertContains(response, smart_str("Memory - Internal RAM: 1.5 GB  %s25.00" % config_value('SHOP', 'CURRENCY')), count=1)
        response = self.client.post(url('satchmo_checkout-step1'), checkout_step1_post_data)
        self.assertRedirects(response, domain + url('DUMMY_satchmo_checkout-step2'), status_code=302, target_status_code=200)
        data = {
            'credit_type': 'Visa',
            'credit_number': '4485079141095836',
            'month_expires': '1',
            'year_expires': '2012',
            'ccv': '552',
            'shipping': 'FlatRate'}
        response = self.client.post(url('DUMMY_satchmo_checkout-step2'), data)
        self.assertRedirects(response, domain + url('DUMMY_satchmo_checkout-step3'), status_code=302, target_status_code=200)
        response = self.client.get(url('DUMMY_satchmo_checkout-step3'))
        self.assertContains(response, smart_str("satchmo computer - %s168.00" % config_value('SHOP', 'CURRENCY')), count=1, status_code=200)
        response = self.client.post(url('DUMMY_satchmo_checkout-step3'), {'process' : 'True'})
        self.assertRedirects(response, domain + url('DUMMY_satchmo_checkout-success'), status_code=302, target_status_code=200)
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

    def test_index(self):
        response = self.client.get('/admin/')
        self.assertContains(response, "auth/user/", status_code=200)

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

