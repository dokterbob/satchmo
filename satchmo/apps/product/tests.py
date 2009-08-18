from decimal import Decimal
from django import db
from django.conf import settings
from django.contrib.sites.models import Site
from django.core import urlresolvers
from django.db.models import Model
from django.http import HttpResponse
from django.test import TestCase
from product.forms import ProductExportForm
from product.models import *
from product.models import Category, ConfigurableProduct, Discount, ProductVariation, Option, OptionGroup, Product, Price
from product.utils import serialize_options, productvariation_details
from StringIO import StringIO
import datetime
import keyedcache
import signals
import zipfile

class OptionGroupTest(TestCase):
    
    def setUp(self):
        self.site=Site.objects.get_current()
        sizes = OptionGroup.objects.create(name="sizes", sort_order=1, site=self.site)
        option_small = Option.objects.create(option_group=sizes, name="Small", value="small", sort_order=1)
        option_large = Option.objects.create(option_group=sizes, name="Large", value="large", sort_order=2, price_change=1)
        colors = OptionGroup.objects.create(name="colors", sort_order=2, site=self.site)
        option_black = Option.objects.create(option_group=colors, name="Black", value="black", sort_order=1)
        option_white = Option.objects.create(option_group=colors, name="White", value="white", sort_order=2, price_change=3)

        # Change an option
        option_white.price_change = 5
        option_white.sort_order = 2
        option_white.save()
        
        self.sizes = sizes
        self.option_small = option_small
        self.option_large = option_large
        self.colors = colors
        self.option_black = option_black
        self.option_white = option_white
        
    def testUniqueTogether(self):
        """You can't have two options with the same value in an option group"""
        self.option_white.value = "black"
        try:
            self.option_white.save()
            self.fail('Should have thrown an error, due to duplicate keys')
        except db.IntegrityError:
            pass
        db.transaction.rollback()
        
    def testValues(self):
        opt = Option.objects.get(id=self.option_white.id)
        self.assertEqual(opt.value, u'white')
        self.assertEqual(opt.price_change, 5)
        self.assertEqual(opt.sort_order, 2)   
        
    def testConfigurable(self):
        """Create a configurable product, testing ordering and price"""
        django_shirt = Product.objects.create(slug="django-shirt", name="Django shirt", site=self.site)
        shirt_price = Price.objects.create(product=django_shirt, price="10.5")
        django_config = ConfigurableProduct.objects.create(product=django_shirt)
        django_config.option_group.add(self.sizes, self.colors)
        ordering = django_config.option_group.order_by('name')
        self.assertEqual(ordering[0], self.colors)
        self.assertEqual(ordering[1], self.sizes)
        django_config.save()

        # Create a product variation
        white_shirt = Product.objects.create(slug="django-shirt_small_white",
            name="Django Shirt (White/Small)", site=self.site)
        pv_white = ProductVariation.objects.create(product=white_shirt, parent=django_config)
        pv_white.options.add(self.option_white, self.option_small)
        self.assertEqual(pv_white.unit_price, Decimal("15.50"))

    def testConfigurableSlugs(self):
        """Create a product with a slug that could conflict with an 
        automatically generated product's slug."""
        
        django_shirt = Product.objects.create(slug="django-shirt", name="Django shirt", site=self.site)
        shirt_price = Price.objects.create(product=django_shirt, price="10.5")
        django_config = ConfigurableProduct.objects.create(product=django_shirt)
        django_config.option_group.add(self.sizes, self.colors)
        django_config.save()
        
        # Create a product with a slug that could conflict with an automatically
        # generated product's slug.
        clash_shirt = Product.objects.create(slug="django-shirt_small_black",
            name="Django Shirt (Black/Small)", site=self.site)

        # Automatically create the rest of the product variations
        django_config.create_subs = True
        django_config.save()
        self.assertEqual(ProductVariation.objects.filter(parent=django_config).count(), 4)

class CategoryTest(TestCase):
    """
    Run some category tests on urls
    """

    def setUp(self):
        self.site = Site.objects.get_current()

    def tearDown(self):
        keyedcache.cache_delete()

#    def test_absolute_url(self):
#        pet_jewelry = Category.objects.create(slug="pet-jewelry", name="Pet Jewelry", site=self.site)
#        womens_jewelry = Category.objects.create(slug="womens-jewelry", name="Women's Jewelry", site=self.site)
#        pet_jewelry.parent = womens_jewelry
#        pet_jewelry.save()
#        womens_jewelry.parent = pet_jewelry
#        self.assertRaises(ValidationError, womens_jewelry.save)
#        Model.save(womens_jewelry)
#        womens_jewelry = Category.objects.active().get(slug="womens-jewelry")
#        url = urlresolvers.reverse('satchmo_category', None, {'parent_slugs', 'womens-jewelry'})
#        self.assertEqual(womens_jewelry.get_absolute_url(), url)

#    def test_infinite_loop(self):
#        """Check that Category methods still work on a Category whose parents list contains an infinite loop."""
#        # Create two Categories that are each other's parents. First make sure that
#        # attempting to save them throws an error, then force a save anyway.
#        pet_jewelry = Category.objects.create(slug="pet-jewelry", name="Pet Jewelry", site=self.site)
#        womens_jewelry = Category.objects.create(slug="womens-jewelry", name="Women's Jewelry", site=self.site)
#        pet_jewelry.parent = womens_jewelry
#        pet_jewelry.save()
#        womens_jewelry.parent = pet_jewelry
#        try:
#            womens_jewelry.save()
#            self.fail('Should have thrown a ValidationError')
#        except ValidationError:
#            pass

#        # force save
#        Model.save(womens_jewelry)
#        pet_jewelry = Category.objects.active().get(slug="pet-jewelry")
#        womens_jewelry = Category.objects.active().get(slug="womens-jewelry")

#        kids = Category.objects.by_site(site=self.site).order_by('name')
#        slugs = [cat.slug for cat in kids]
#        self.assertEqual(slugs, [u'pet-jewelry', u'womens-jewelry'])

class DiscountTest(TestCase):

    def setUp(self):
        self.site = Site.objects.get_current()
        start = datetime.date(2006, 10, 1)
        end = datetime.date(5000, 10, 1)
        self.discount = Discount.objects.create(description="New Sale", code="BUYME", amount="5.00", allowedUses=10,
            numUses=0, minOrder=5, active=True, startDate=start, endDate=end, shipping='NONE', site=self.site)
    
    def tearDown(self):
        keyedcache.cache_delete()
    
    def testValid(self):

        v = self.discount.isValid()
        self.assert_(v[0])
        self.assertEqual(v[1], u'Valid.')

    def testFutureDate(self):
        """Test a future date for discount start"""
        start = datetime.date(5000, 1, 1)
        self.discount.startDate = start
        self.discount.save()
        self.discount.isValid()
        v = self.discount.isValid()
        self.assertFalse(v[0])
        self.assertEqual(v[1], u'This coupon is not active yet.')

    def testPastDate(self):
        """Test an expired discount"""
        #Change end date to the past
        start = datetime.date(2000, 1, 1)
        end = datetime.date(2006, 1, 1)
        self.discount.startDate = start
        self.discount.endDate = end
        self.discount.save()
        v = self.discount.isValid()
        self.assertFalse(v[0])
        self.assertEqual(v[1], u'This coupon has expired.')

    def testNotActive(self):
        """Not active should always be invalid."""
        self.discount.startDate = datetime.date(2006, 12, 1)
        self.discount.endDate = datetime.date(5000, 12, 1)
        self.discount.active = False
        self.discount.save()
        v = self.discount.isValid()
        self.assertFalse(v[0], False)
        self.assertEqual(v[1], u'This coupon is disabled.')
                

class CalcFunctionTest(TestCase):
    
    def testEvenSplit1(self):
        """Simple split test"""
        d = {
            1 : Decimal("10.00"),
            2 : Decimal("10.00"),
            3 : Decimal("10.00"),
            4 : Decimal("10.00"),
        }
        
        s = Discount.apply_even_split(d, Decimal("16.00"))
        self.assertEqual(s[1], Decimal("4.00"))
        self.assertEqual(s[2], Decimal("4.00"))
        self.assertEqual(s[3], Decimal("4.00"))
        self.assertEqual(s[4], Decimal("4.00"))
        
    def testEvenSplitTooMuch(self):
        """Test when amount is greater than total"""
        d = {
            1 : Decimal("10.00"),
            2 : Decimal("10.00"),
            3 : Decimal("10.00"),
            4 : Decimal("10.00"),
        }
        
        s = Discount.apply_even_split(d, Decimal("50.00"))
        self.assertEqual(s[1], Decimal("10.00"))
        self.assertEqual(s[2], Decimal("10.00"))
        self.assertEqual(s[3], Decimal("10.00"))
        self.assertEqual(s[4], Decimal("10.00"))

    def testEvenSplitEqual(self):
        """Test when amount is exactly equal"""
        d = {
            1 : Decimal("10.00"),
            2 : Decimal("10.00"),
            3 : Decimal("10.00"),
            4 : Decimal("10.00"),
        }

        s = Discount.apply_even_split(d, Decimal("40.00"))
        self.assertEqual(s[1], Decimal("10.00"))
        self.assertEqual(s[2], Decimal("10.00"))
        self.assertEqual(s[3], Decimal("10.00"))
        self.assertEqual(s[4], Decimal("10.00"))
        
        
    def testEvenSplitOneTooSmall(self):
        """Test when one of the items is maxed, but others are OK"""
        d = {
            1 : Decimal("10.00"),
            2 : Decimal("5.00"),
            3 : Decimal("10.00"),
            4 : Decimal("10.00"),
        }

        s = Discount.apply_even_split(d, Decimal("23.00"))
        self.assertEqual(s[1], Decimal("6.00"))
        self.assertEqual(s[2], Decimal("5.00"))
        self.assertEqual(s[3], Decimal("6.00"))
        self.assertEqual(s[4], Decimal("6.00"))

    def testThirds(self):
        d = {
            1 : Decimal("10.00"),
            2 : Decimal("10.00"),
            3 : Decimal("10.00"),
        }

        s = Discount.apply_even_split(d, Decimal("10.00"))
        self.assertEqual(s[1], Decimal("3.33"))
        self.assertEqual(s[2], Decimal("3.33"))
        self.assertEqual(s[3], Decimal("3.33"))


    def testThirdsUneven(self):
        d = {
            1 : Decimal("10.00"),
            2 : Decimal("10.00"),
            3 : Decimal("3.00"),
        }

        s = Discount.apply_even_split(d, Decimal("10.00"))
        self.assertEqual(s[1], Decimal("3.50"))
        self.assertEqual(s[2], Decimal("3.50"))
        self.assertEqual(s[3], Decimal("3.00"))


    def testPercentage1(self):
        d = {
            1 : Decimal("10.00"),
            2 : Decimal("10.00"),
            3 : Decimal("10.00"),
        }

        s = Discount.apply_percentage(d, Decimal("10.00"))
        self.assertEqual(s[1], Decimal("1.00"))
        self.assertEqual(s[2], Decimal("1.00"))
        self.assertEqual(s[3], Decimal("1.00"))


class ProductExportTest(TestCase):
    """
    Test product export functionality.
    """

    def setUp(self):
        # Log in as a superuser
        from django.contrib.auth.models import User
        user = User.objects.create_user('root', 'root@eruditorum.com', '12345')
        user.is_staff = True
        user.is_superuser = True
        user.save()
        self.client.login(username='root', password='12345')
        
    def tearDown(self):
        keyedcache.cache_delete()

    def test_text_export(self):
        """
        Test the content type of an exported text file.
        """
        url = urlresolvers.reverse('satchmo_admin_product_export')

        form_data = {
            'format': 'yaml',
            'include_images': False,
        }

        response = self.client.post(url, form_data)
        self.assertTrue(response.has_header('Content-Type'))
        self.assertEqual('text/yaml', response['Content-Type'])

        form_data['format'] = 'json'
        response = self.client.post(url, form_data)
        self.assertTrue(response.has_header('Content-Type'))
        self.assertEqual('text/json', response['Content-Type'])

        form_data['format'] = 'xml'
        response = self.client.post(url, form_data)
        self.assertTrue(response.has_header('Content-Type'))
        self.assertEqual('text/xml', response['Content-Type'])

        form_data['format'] = 'python'
        response = self.client.post(url, form_data)
        self.assertTrue(response.has_header('Content-Type'))
        self.assertEqual('text/python', response['Content-Type'])

    def test_zip_export_content_type(self):
        """
        Test the content type of an exported zip file.
        """
        url = urlresolvers.reverse('satchmo_admin_product_export')
        form_data = {
            'format': 'yaml',
            'include_images': True,
        }

        response = self.client.post(url, form_data)
        self.assertTrue(response.has_header('Content-Type'))
        self.assertEqual('application/zip', response['Content-Type'])
        
    def test_unicode(self):
        """Test the ProductExportForm behavior
        Specifically, we're checking that a unicode 'format' is converted to ascii
        in the 'export' method of 'ProductExportForm'."""
        form = ProductExportForm({'format': u'yaml', 'include_images': True})
        response = form.export(None)
        self.assert_(isinstance(response, HttpResponse))

class ProductTest(TestCase):
    """Test Product functions"""
    fixtures = ['l10n-data.yaml','sample-store-data.yaml', 'products.yaml', 'test-config.yaml']

    def tearDown(self):
        keyedcache.cache_delete()

    def test_quantity_price_standard_product(self):
        """Check quantity price for a standard product"""

        product = Product.objects.get(slug='PY-Rocks')
        self.assertEqual(product.unit_price, Decimal("19.50"))

    def test_discount_qty_price(self):
        """Test quantity price discounts"""
        product = Product.objects.get(slug='PY-Rocks')
        price = Price(product=product, quantity=Decimal('10'), price=Decimal("10.00"))
        price.save()

        self.assertEqual(product.unit_price, Decimal("19.50"))
        self.assertEqual(product.get_qty_price(Decimal('1')), Decimal("19.50"))
        self.assertEqual(product.get_qty_price(Decimal('2')), Decimal("19.50"))
        self.assertEqual(product.get_qty_price(Decimal('10')), Decimal("10.00"))
        
    def test_expiring_price(self):
        """Test whether a price with an expiration date is used in preference to a non-expiring price."""
        product = Product.objects.get(slug='PY-Rocks')
        self.assertEqual(product.unit_price, Decimal("19.50"))

        today = datetime.datetime.now()
        aweek = datetime.timedelta(days=7)
        lastwk = today - aweek
        nextwk = today + aweek

        # new price should override the old one
        price = Price.objects.create(product=product, quantity=Decimal('1'), price=Decimal("10.00"), expires=nextwk)
        self.assertEqual(product.unit_price, Decimal("10.00"))

        # but not if it is expired
        price.expires = lastwk
        price.save()
        self.assertEqual(product.unit_price, Decimal("19.50"))

    def test_quantity_price_productvariation(self):
        """Check quantity price for a productvariation"""

        # base product
        product = Product.objects.get(slug='dj-rocks')
        self.assertEqual(product.unit_price, Decimal("20.00"))
        self.assertEqual(product.unit_price, product.get_qty_price(Decimal('1')))

        # product with no price delta
        product = Product.objects.get(slug='dj-rocks-s-b')
        self.assertEqual(product.unit_price, Decimal("20.00"))
        self.assertEqual(product.unit_price, product.get_qty_price(Decimal('1')))

        # product which costs more due to details
        product = Product.objects.get(slug='dj-rocks-l-bl')
        self.assertEqual(product.unit_price, Decimal("23.00"))
        self.assertEqual(product.unit_price, product.get_qty_price(Decimal('1')))


    def test_quantity_price_productvariation_expiring(self):
        """Check expiring quantity price for a productvariation"""

        # base product
        product = Product.objects.get(slug='dj-rocks')
        self.assertEqual(product.unit_price, Decimal("20.00"))
        self.assertEqual(product.unit_price, product.get_qty_price(Decimal('1')))

        today = datetime.datetime.now()
        aweek = datetime.timedelta(days=7)
        nextwk = today + aweek

        # new price should override the old one
        price = Price.objects.create(product=product, quantity=Decimal('1'), price=Decimal("10.00"), expires=nextwk)
        self.assertEqual(product.unit_price, Decimal("10.00"))

        # product with no price delta
        product = Product.objects.get(slug='dj-rocks-s-b')
        self.assertEqual(product.unit_price, Decimal("10.00"))

        # product which costs more due to details
        product = Product.objects.get(slug='dj-rocks-l-bl')
        self.assertEqual(product.unit_price, Decimal("13.00"))

        # now test explicit expiring price on a product variation
        pvprice = Price.objects.create(product=product, quantity=Decimal('1'), price=Decimal("5.00"), expires=nextwk)
        self.assertEqual(product.unit_price, Decimal("5.00"))

    def test_smart_attr(self):
        p = Product.objects.get(slug__iexact='dj-rocks')
        mb = Product.objects.get(slug__iexact='dj-rocks-m-b')
        sb = Product.objects.get(slug__iexact='dj-rocks-s-b')

        # going to set a weight on the product, and an override weight on the medium
        # shirt.

        p.weight = 100
        p.save()
        sb.weight = 50
        sb.save()

        self.assertEqual(p.smart_attr('weight'), 100)
        self.assertEqual(sb.smart_attr('weight'), 50)
        self.assertEqual(mb.smart_attr('weight'), 100)

        # no height
        self.assertEqual(p.smart_attr('height'), None)
        self.assertEqual(sb.smart_attr('height'), None)

class ConfigurableProductTest(TestCase):
    """Test ConfigurableProduct."""
    fixtures = ['products.yaml']
    
    def tearDown(self):
        keyedcache.cache_delete()

    def test_get_variations_for_options(self):
        # Retrieve the objects.
        dj_rocks = ConfigurableProduct.objects.get(product__slug="dj-rocks")
        option_small = Option.objects.get(pk=1)
        option_black = Option.objects.get(pk=4)
        option_hard_cover = Option.objects.get(pk=7)

        # Test filtering for one valid option.
        self.assertEqual([variation.pk for variation in
            dj_rocks.get_variations_for_options([option_small])], [6, 7, 8])
        # Test filtering for two valid options.
        self.assertEqual([variation.pk for variation in
            dj_rocks.get_variations_for_options([option_small, option_black])],
            [6])
        # Test filtering for an option that cannot apply to the product.
        self.assertEqual(
            len(dj_rocks.get_variations_for_options([option_hard_cover])), 0)
        # Test filtering for nothing.
        self.assertEqual([variation.pk for variation in
            dj_rocks.get_variations_for_options([])],
            [6, 7, 8, 9, 10, 11, 12, 13, 14])

class OptionUtilsTest(TestCase):
    """Test the utilities used for serialization of options and selected option details."""
    fixtures = ['products.yaml']
    
    def test_base_sort_order(self):
        p = Product.objects.get(slug='dj-rocks')
        serialized = serialize_options(p.configurableproduct)
        self.assert_(len(serialized), 2)
        self.assertEqual(serialized[0]['id'], 1)
        got_vals = [opt.value for opt in serialized[0]['items']]
        self.assertEqual(got_vals, ['S','M','L'])
        self.assertEqual(serialized[1]['id'], 2)

    def test_reordered(self):
        p = Product.objects.get(slug='dj-rocks')
        
        pv = p.configurableproduct.productvariation_set.all()[0]
        orig_key = pv.optionkey
        orig_detl = productvariation_details(p, False, None, create=True)
        
        sizegroup = OptionGroup.objects.get(name="sizes")
        sizegroup.sort_order = 100
        sizegroup.save()
        
        # reverse ordering
        for opt in sizegroup.option_set.all():
            opt.sort_order = 100-opt.sort_order
            opt.save()
        
        serialized = serialize_options(p.configurableproduct)
        self.assert_(len(serialized), 2)
        self.assertEqual(serialized[1]['id'], 1)
        got_vals = [opt.value for opt in serialized[1]['items']]
        self.assertEqual(got_vals, ['L','M','S'])
        
        pv2 = ProductVariation.objects.get(pk=pv.pk)
        self.assertEqual(orig_key, pv2.optionkey)
        reorder_detl = productvariation_details(p, False, None)
        self.assertEqual(orig_detl, reorder_detl)

class PriceAdjustmentTest(TestCase):
    fixtures = ['products.yaml']
    
    def setUp(self):
        self.product = Product.objects.get(slug="dj-rocks")
        self.price = self.product.price_set.get(quantity=1)
        
    def tearDown(self):
        keyedcache.cache_delete()
            
    def test_basic(self):
        pcalc = PriceAdjustmentCalc(self.price)
        p = PriceAdjustment('test', amount=Decimal(1))
        pcalc += p
        pcalc += p
        p = PriceAdjustment('test2', amount=Decimal(10))
        pcalc += p
        self.assertEqual(pcalc.total_adjustment(), Decimal(12))
        
    def test_product_adjustments(self):
        p1 = self.product.unit_price
        self.assertEqual(p1, Decimal('20.00'))
        signals.satchmo_price_query.connect(five_off)
        p2 = self.product.unit_price
        self.assertEqual(p2, Decimal('15.00'))
        adj = get_product_quantity_adjustments(self.product, qty=1)
        self.assertEqual(len(adj.adjustments), 1)
        a = adj.adjustments[0]
        self.assertEqual(a.key, 'half')
        self.assertEqual(a.amount, Decimal(5))
        signals.satchmo_price_query.disconnect(five_off)

def five_off(sender, adjustment=None, **kwargs):
    adjustment += PriceAdjustment('half', 'Half', amount=Decimal(5))

if __name__ == "__main__":
    import doctest
    doctest.testmod()

