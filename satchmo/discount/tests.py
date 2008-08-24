import datetime
try:
    from decimal import Decimal
except:
    from django.utils._decimal import Decimal

from django.test import TestCase
from models import *
from satchmo.caching import cache_delete
from satchmo.configuration import config_get
from satchmo.contact.models import AddressBook, Contact
from satchmo.l10n.models import Country
from satchmo.product.models import Product
from satchmo.shop.models import Order, OrderItem
from django.contrib.sites.models import Site

class DiscountTest(TestCase):
    #fixtures = ['test_shop.yaml']

    def setUp(self):
        self.site = Site.objects.get_current()
        start = datetime.date(2006, 10, 1)
        end = datetime.date(5000, 10, 1)
        self.discount = Discount.objects.create(description="New Sale", code="BUYME", amount="5.00", allowedUses=10,
            numUses=0, minOrder=5, active=True, startDate=start, endDate=end, freeShipping=False, site=self.site)
    
    def tearDown(self):
        cache_delete()
    
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
        
        s = apply_even_split(d, Decimal("16.00"))
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
        
        s = apply_even_split(d, Decimal("50.00"))
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

        s = apply_even_split(d, Decimal("40.00"))
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

        s = apply_even_split(d, Decimal("23.00"))
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

        s = apply_even_split(d, Decimal("10.00"))
        self.assertEqual(s[1], Decimal("3.33"))
        self.assertEqual(s[2], Decimal("3.33"))
        self.assertEqual(s[3], Decimal("3.33"))


    def testThirdsUneven(self):
        d = {
            1 : Decimal("10.00"),
            2 : Decimal("10.00"),
            3 : Decimal("3.00"),
        }

        s = apply_even_split(d, Decimal("10.00"))
        self.assertEqual(s[1], Decimal("3.50"))
        self.assertEqual(s[2], Decimal("3.50"))
        self.assertEqual(s[3], Decimal("3.00"))


    def testPercentage1(self):
        d = {
            1 : Decimal("10.00"),
            2 : Decimal("10.00"),
            3 : Decimal("10.00"),
        }

        s = apply_percentage(d, Decimal("10.00"))
        self.assertEqual(s[1], Decimal("1.00"))
        self.assertEqual(s[2], Decimal("1.00"))
        self.assertEqual(s[3], Decimal("1.00"))
        
class DiscountAmountTest(TestCase):
    fixtures = ['l10n-data.yaml', 'test_discount.yaml']
    
    def setUp(self):
        self.US = Country.objects.get(iso2_code__iexact = 'US')
        self.site = Site.objects.get_current()
        tax = config_get('TAX','MODULE')
        tax.update('satchmo.tax.modules.no')
        c = Contact(first_name="Jim", last_name="Tester", 
            role="Customer", email="Jim@JimWorld.com")
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
        item1 = OrderItem(order=o, product=p, quantity=1,
            unit_price=price, line_item_price=price)
        item1.save()
        
        item1s = OrderItem(order=small, product=p, quantity=1,
            unit_price=price, line_item_price=price)
        item1s.save()
        
        p = Product.objects.get(slug='neat-book-hard')
        price = p.unit_price
        item2 = OrderItem(order=o, product=p, quantity=1,
            unit_price=price, line_item_price=price)
        item2.save()
        self.order = o
        self.small = small

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
        self.assertEqual(price, Decimal('7.01'))
        self.assertEqual(shipcost, Decimal('6.00'))
        self.assertEqual(shiptotal, Decimal('2.67'))
        self.assertEqual(discount, Decimal('9.99'))

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

        self.assertEqual(sub_total, Decimal('11.00'))
        self.assertEqual(price, Decimal('1.00'))
        self.assertEqual(shipcost, Decimal('6.00'))
        self.assertEqual(shiptotal, Decimal('0.00'))
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
        

