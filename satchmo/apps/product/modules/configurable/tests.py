from decimal import Decimal
from django.contrib.sites.models import Site
from django.test import TestCase
from product.models import Option, OptionGroup, Product, Price
from product.modules.configurable.models import ConfigurableProduct, ProductVariation
import datetime
import keyedcache
from product.utils import serialize_options, productvariation_details


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


class ProductTest(TestCase):
    """Test Product functions"""
    fixtures = ['l10n-data.yaml','sample-store-data.yaml', 'products.yaml', 'test-config.yaml']

    def tearDown(self):
        keyedcache.cache_delete()

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


if __name__ == "__main__":
    import doctest
    doctest.testmod()

