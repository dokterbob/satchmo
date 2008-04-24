from django.test import TestCase
from django.test.client import Client
from django.core.urlresolvers import reverse as url
from django.conf import settings
from django.contrib.auth.models import User
from django.utils.encoding import smart_str
from satchmo.caching import cache_delete
from satchmo.contact.models import Contact
from satchmo.product.models import Product
from satchmo.shop.templatetags import get_filter_args
from satchmo.configuration import config_value, config_get
from satchmo.wishlist.models import *

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

class WishTest(TestCase):
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

    def test_wish_adding_not_logged_in(self):
        """
        Validate we can't add unless we are logged in.
        """
        response = self.client.get(prefix+'/product/DJ-Rocks/')
        self.assertContains(response, "Django Rocks shirt", count=2, status_code=200)
        response = self.client.post(prefix+'/add/', { 
            "productname" : "DJ-Rocks",
            "1" : "M",
            "2" : "BL",
            "addwish" : "Add to wishlist"
        })
        self.assertContains(response, "Sorry, you must be", count=1, status_code=200)
    
class WishTestLoggedIn(TestCase):
    fixtures = ['l10n-data.yaml', 'sample-store-data.yaml', 'products.yaml', 'test-config.yaml']
    
    def setUp(self):
        self.client = Client()
        user = User.objects.create_user('wisher', 'wisher@example.com', 'passwd')
        user.is_staff = False
        user.is_superuser = False
        user.save()
        self.contact = Contact.objects.create(user=user, first_name="Wish",
            last_name="Tester")
        self.client.login(username='wisher', password='passwd')
        
    def test_wish_adding(self):
        """
        Validate we can add some items to the wishlist
        """
        response = self.client.get(prefix+'/product/DJ-Rocks/')
        self.assertContains(response, "Django Rocks shirt", count=2, status_code=200)
        response = self.client.post(prefix+'/add/', { 
            "productname" : "DJ-Rocks",
            "1" : "M",
            "2" : "BL",
            "addwish" : "Add to wishlist"
        })
        self.assertRedirects(response, domain + prefix+'/wishlist/', status_code=302, target_status_code=200)
        response = self.client.get(prefix+'/wishlist/')
        
        self.assertContains(response, "Django Rocks shirt (Medium/Blue)", count=1, status_code=200)

    def test_wish_removing(self):
        """
        Validate that we can remove wishlist items
        """
        product = Product.objects.get(slug="DJ-Rocks_M_BL")
        wish = ProductWish(product = product, contact=self.contact)
        wish.save()
        
        product = Product.objects.get(slug="robot-attack_soft")
        wish = ProductWish(product = product, contact=self.contact)
        wish.save()
        
        response = self.client.get(prefix+'/wishlist/')
        self.assertContains(response, "Robots Attack", count=1, status_code=200)
        self.assertContains(response, "Django Rocks shirt (Medium/Blue)", count=1, status_code=200)
        
        response = self.client.post(prefix+'/wishlist/remove/', {
            'id' : wish.id
        })
        self.assertContains(response, "Robots Attack", count=0, status_code=200)
        self.assertContains(response, "Django Rocks shirt (Medium/Blue)", count=1, status_code=200)

    def test_wish_to_cart(self):
        """
        Validate that we can move an item to the cart
        """
        product = Product.objects.get(slug="DJ-Rocks_M_BL")
        wish = ProductWish(product = product, contact=self.contact)
        wish.save()
        
        product = Product.objects.get(slug="robot-attack_soft")
        wish = ProductWish(product = product, contact=self.contact)
        wish.save()
        
        response = self.client.get(prefix+'/wishlist/')
        self.assertContains(response, "Robots Attack", count=1, status_code=200)
        self.assertContains(response, "Django Rocks shirt (Medium/Blue)", count=1, status_code=200)
        
        response = self.client.post(prefix+'/wishlist/add_cart/', {
            'id' : wish.id
        })
        self.assertRedirects(response, domain + prefix+'/cart/', status_code=302, target_status_code=200)
        response = self.client.get(prefix+'/cart/')
        self.assertContains(response, "Robots Attack", count=1, status_code=200)
        
        