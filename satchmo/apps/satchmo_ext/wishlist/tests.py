from django.conf import settings
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse as url
from django.test import TestCase
from django.test.client import Client
from django.utils.encoding import smart_str
from keyedcache import cache_delete
from l10n.models import Country
from livesettings import config_value, config_get
from product.models import Product
from product.utils import rebuild_pricing
from satchmo_ext.wishlist.models import *
from satchmo_store.contact.models import Contact
from satchmo_utils.templatetags import get_filter_args

domain = 'http://testserver'

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
        'paymentmethod': 'DUMMY'
    }

class WishTest(TestCase):
    fixtures = ['l10n-data.yaml', 'sample-store-data.yaml', 'products.yaml', 'test-config.yaml']

    def setUp(self):
        # Every test needs a client
        self.client = Client()
        rebuild_pricing()

    def tearDown(self):
        cache_delete()

    def test_main_page(self):
        """
        Look at the main page
        """
        response = self.client.get(url('satchmo_shop_home'))

        # Check that the rendered context contains 4 products
        self.assertContains(response, '<div class = "productImage">',
                            count=4, status_code=200)

    def test_wish_adding_not_logged_in(self):
        """
        Validate we can't add unless we are logged in.
        """
        product = Product.objects.get(slug='dj-rocks')
        response = self.client.get(product.get_absolute_url())
        self.assertContains(response, "Django Rocks shirt", count=2, status_code=200)
        response = self.client.post(url('satchmo_smart_add'), { 
            "productname" : "dj-rocks",
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
        rebuild_pricing()
        
    def tearDown(self):
        cache_delete()
        
    def test_wish_adding(self):
        """
        Validate we can add some items to the wishlist
        """
        product = Product.objects.get(slug='dj-rocks')
        response = self.client.get(product.get_absolute_url())
        self.assertContains(response, "Django Rocks shirt", count=2, status_code=200)
        response = self.client.post(url('satchmo_smart_add'), { 
            "productname" : "dj-rocks",
            "1" : "M",
            "2" : "BL",
            "addwish" : "Add to wishlist"
        })
        wishurl = url('satchmo_wishlist_view')
        self.assertRedirects(response, domain + wishurl, status_code=302, target_status_code=200)
        response = self.client.get(wishurl)
        
        self.assertContains(response, "Django Rocks shirt (Medium/Blue)", count=1, status_code=200)

    def test_wish_removing(self):
        """
        Validate that we can remove wishlist items
        """
        product = Product.objects.get(slug="dj-rocks-m-bl")
        wish = ProductWish(product = product, contact=self.contact)
        wish.save()
        
        product = Product.objects.get(slug="robot-attack-soft")
        wish = ProductWish(product = product, contact=self.contact)
        wish.save()
        
        wishurl = url('satchmo_wishlist_view')
        response = self.client.get(wishurl)
        self.assertContains(response, "Robots Attack", count=1, status_code=200)
        self.assertContains(response, "Django Rocks shirt (Medium/Blue)", count=1, status_code=200)
        
        wishurl = url('satchmo_wishlist_remove')
        response = self.client.post(wishurl, {
            'id' : wish.id
        })
        self.assertContains(response, "Robots Attack", count=0, status_code=200)
        self.assertContains(response, "Django Rocks shirt (Medium/Blue)", count=1, status_code=200)

    def test_wish_to_cart(self):
        """
        Validate that we can move an item to the cart
        """
        product = Product.objects.get(slug="dj-rocks-m-bl")
        wish = ProductWish(product = product, contact=self.contact)
        wish.save()
        
        product = Product.objects.get(slug="robot-attack-soft")
        wish = ProductWish(product = product, contact=self.contact)
        wish.save()
        
        wishurl = url('satchmo_wishlist_view')
        response = self.client.get(wishurl)
        self.assertContains(response, "Robots Attack", count=1, status_code=200)
        self.assertContains(response, "Django Rocks shirt (Medium/Blue)", count=1, status_code=200)
        
        moveurl = url('satchmo_wishlist_move_to_cart')
        response = self.client.post(moveurl, {
            'id' : wish.id
        })
        carturl = url('satchmo_cart')
        self.assertRedirects(response, domain + carturl, status_code=302, target_status_code=200)

        response = self.client.get(carturl)
        self.assertContains(response, "Robots Attack", count=1, status_code=200)
        
        