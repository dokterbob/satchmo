r"""
>>> try:
...     from decimal import Decimal
... except:
...     from django.utils._decimal import Decimal

>>> from django import db
>>> from django.db.models import Model
>>> from satchmo.product.models import *

# Create option groups and their options
>>> sizes = OptionGroup.objects.create(name="sizes", sort_order=1)
>>> option_small = Option.objects.create(optionGroup=sizes, name="Small", value="small", displayOrder=1)
>>> option_large = Option.objects.create(optionGroup=sizes, name="Large", value="large", displayOrder=2, price_change=1)
>>> colors = OptionGroup.objects.create(name="colors", sort_order=2)
>>> option_black = Option.objects.create(optionGroup=colors, name="Black", value="black", displayOrder=1)
>>> option_white = Option.objects.create(optionGroup=colors, name="White", value="white", displayOrder=2, price_change=3)

# Change an option
>>> option_white.price_change = 5
>>> option_white.displayOrder = 2
>>> option_white.save()

# You can't have two options with the same value in an option group
>>> option_white.value = "black"
>>> try:
...     option_white.save()
...     assert False
... except db.IntegrityError: pass
>>> db.transaction.rollback()

# Check the values that were saved to the database
>>> option_white = Option.objects.get(id=option_white.id)
>>> ((option_white.value, option_white.price_change, option_white.displayOrder)
... == (u'white', 5, 2))
True

# Create a configurable product
>>> django_shirt = Product.objects.create(slug="django-shirt", name="Django shirt")
>>> shirt_price = Price.objects.create(product=django_shirt, price="10.5")
>>> django_config = ConfigurableProduct.objects.create(product=django_shirt)
>>> django_config.option_group.add(sizes, colors)
>>> django_config.option_group.order_by('name')
[<OptionGroup: colors>, <OptionGroup: sizes>]
>>> django_config.save()

# Create a product variation
>>> white_shirt = Product.objects.create(slug="django-shirt_small_white", name="Django Shirt (White/Small)")
>>> pv_white = ProductVariation.objects.create(product=white_shirt, parent=django_config)
>>> pv_white.options.add(option_white, option_small)
>>> pv_white.unit_price == Decimal("15.50")
True

# Create a product with a slug that could conflict with an automatically
# generated product's slug.
>>> clash_shirt = Product.objects.create(slug="django-shirt_small_black", name="Django Shirt (Black/Small)")

# Automatically create the rest of the product variations
>>> django_config.create_subs = True
>>> django_config.save()
>>> ProductVariation.objects.filter(parent=django_config).count()
4

# Test the ProductExportForm behavior
# Specifically, we're checking that a unicode 'format' is converted to ascii
# in the 'export' method of 'ProductExportForm'.
>>> import zipfile
>>> from StringIO import StringIO
>>> from satchmo.product.forms import ProductExportForm
>>> form = ProductExportForm({'format': u'yaml', 'include_images': True})
>>> form.export(None)
<django.http.HttpResponse object at ...>
"""

from django.conf import settings
from django.core.validators import ValidationError
from django.db.models import Model
from django.test import TestCase
from satchmo.product.models import Category, ConfigurableProduct, Option, Product, Price
try:
    from decimal import Decimal
except ImportError:
    from django.utils._decimal import Decimal


class CategoryTest(TestCase):
    """
    Run some category tests on urls
    """

    def test_absolute_url(self):
        prefix = settings.SHOP_BASE
        if prefix == '/':
            prefix = ''
        pet_jewelry = Category.objects.create(slug="pet-jewelry", name="Pet Jewelry")
        womens_jewelry = Category.objects.create(slug="womens-jewelry", name="Women's Jewelry")
        pet_jewelry.parent = womens_jewelry
        pet_jewelry.save()
        womens_jewelry.parent = pet_jewelry
        self.assertRaises(ValidationError, womens_jewelry.save)
        Model.save(womens_jewelry)
        womens_jewelry = Category.objects.get(slug="womens-jewelry")
        self.assertEqual(womens_jewelry.get_absolute_url(), (u"%s/category/womens-jewelry/pet-jewelry/womens-jewelry/" % prefix))

    def test_infinite_loop(self):
        """Check that Category methods still work on a Category whose parents list contains an infinite loop."""
        # Create two Categories that are each other's parents. First make sure that
        # attempting to save them throws an error, then force a save anyway.
        pet_jewelry = Category.objects.create(slug="pet-jewelry", name="Pet Jewelry")
        womens_jewelry = Category.objects.create(slug="womens-jewelry", name="Women's Jewelry")
        pet_jewelry.parent = womens_jewelry
        pet_jewelry.save()
        womens_jewelry.parent = pet_jewelry
        try:
            womens_jewelry.save()
            self.fail('Should have thrown a ValidationError')
        except ValidationError:
            pass

        # force save
        Model.save(womens_jewelry)
        pet_jewelry = Category.objects.get(slug="pet-jewelry")
        womens_jewelry = Category.objects.get(slug="womens-jewelry")

        kids = Category.objects.all().order_by('name')
        slugs = [cat.slug for cat in kids]
        self.assertEqual(slugs, [u'pet-jewelry', u'womens-jewelry'])

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

    def test_text_export(self):
        """
        Test the content type of an exported text file.
        """
        url = '%s/product/inventory/export/' % settings.SHOP_BASE
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
        url = '%s/product/inventory/export/' % settings.SHOP_BASE
        form_data = {
            'format': 'yaml',
            'include_images': True,
        }

        response = self.client.post(url, form_data)
        self.assertTrue(response.has_header('Content-Type'))
        self.assertEqual('application/zip', response['Content-Type'])

class ProductTest(TestCase):
    """Test Product functions"""
    fixtures = ['sample-store-data.yaml', 'products.yaml', 'test-config.yaml']

    def test_quantity_price_standard_product(self):
        """Check quantity price for a standard product"""

        product = Product.objects.get(slug='PY-Rocks')
        self.assertEqual(product.unit_price, Decimal("19.50"))

    def test_discount_qty_price(self):
        """Test quantity price discounts"""
        product = Product.objects.get(slug='PY-Rocks')
        price = Price(product=product, quantity=10, price=Decimal("10.00"))
        price.save()

        self.assertEqual(product.unit_price, Decimal("19.50"))
        self.assertEqual(product.get_qty_price(1), Decimal("19.50"))
        self.assertEqual(product.get_qty_price(2), Decimal("19.50"))
        self.assertEqual(product.get_qty_price(10), Decimal("10.00"))

    def test_quantity_price_productvariation(self):
        """Check quantity price for a productvariation"""

        # base product
        product = Product.objects.get(slug='DJ-Rocks')
        self.assertEqual(product.unit_price, Decimal("20.00"))
        self.assertEqual(product.unit_price, product.get_qty_price(1))

        # product with no price delta
        product = Product.objects.get(slug='DJ-Rocks_S_B')
        self.assertEqual(product.unit_price, Decimal("20.00"))
        self.assertEqual(product.unit_price, product.get_qty_price(1))

        # product which costs more due to details
        product = Product.objects.get(slug='DJ-Rocks_L_BL')
        self.assertEqual(product.unit_price, Decimal("23.00"))
        self.assertEqual(product.unit_price, product.get_qty_price(1))

    def test_smart_attr(self):
        p = Product.objects.get(slug__iexact='DJ-Rocks')
        mb = Product.objects.get(slug__iexact='DJ-Rocks_M_B')
        sb = Product.objects.get(slug__iexact='DJ-Rocks_S_B')

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

    def test_get_variations_for_options(self):
        dj_rocks = ConfigurableProduct.objects.get(product__slug="DJ-Rocks")
        option_small = Option.objects.get(pk=1)
        option_black = Option.objects.get(pk=4)
        option_hard_cover = Option.objects.get(pk=7)

        self.assertEqual([variation.pk for variation in
            dj_rocks.get_variations_for_options([option_small])], [6, 7, 8])
        self.assertEqual(
            len(dj_rocks.get_variations_for_options([option_hard_cover])), 0)
        self.assertEqual([variation.pk for variation in
            dj_rocks.get_variations_for_options([option_small, option_black])],
            [6])

if __name__ == "__main__":
    import doctest
    doctest.testmod()

