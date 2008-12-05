"""
Sets up a discount that can be applied to a product
"""

try:
    from decimal import Decimal
except:
    from django.utils._decimal import Decimal

from django.contrib.sites.models import Site
from django.db import models
from django.utils.translation import ugettext, ugettext_lazy as _
from satchmo.l10n.utils import moneyfmt
from satchmo.product.models import Product, ProductPriceLookup
import datetime
import logging
import operator

log = logging.getLogger('Discount.models')


class NullDiscount(object):

    def __init__(self):
        self.description = _("No Discount")
        self.total = Decimal("0.00")
        self.item_discounts = {}
        self.discounted_prices = []
        self.automatic = False

    def calc(self, *args):
        return Decimal("0.00")

class Discount(models.Model):
    """
    Allows for multiple types of discounts including % and dollar off.
    Also allows finite number of uses.
    """
    site = models.ForeignKey(Site, verbose_name=_('site'))
    description = models.CharField(_("Description"), max_length=100)
    code = models.CharField(_("Discount Code"), max_length=20, unique=True,
        help_text=_("Coupon Code"))
    amount = models.DecimalField(_("Discount Amount"), decimal_places=2,
        max_digits=4, blank=True, null=True, 
        #validator_list=[amount_validator],
        help_text=_("Enter absolute discount amount OR percentage."))
    percentage = models.DecimalField(_("Discount Percentage"), decimal_places=2,
        max_digits=4, blank=True, null=True,
        #validator_list=[percentage_validator],
        help_text=_("Enter absolute discount amount OR percentage.  Percentage example: \"0.10\"."))
    automatic = models.BooleanField(_("Is this an automatic discount?"), default=False, blank=True,
        null=True, help_text=_("Use this field to advertise the discount on all products to which it applies.  Generally this is used for site-wide sales."))
    allowedUses = models.IntegerField(_("Number of allowed uses"),
        blank=True, null=True, help_text=_('Not implemented.'))
    numUses = models.IntegerField(_("Number of times already used"),
        blank=True, null=True, help_text=_('Not implemented.'))
    minOrder = models.DecimalField(_("Minimum order value"),
        decimal_places=2, max_digits=6, blank=True, null=True)
    startDate = models.DateField(_("Start Date"))
    endDate = models.DateField(_("End Date"))
    active = models.BooleanField(_("Active"))
    freeShipping = models.BooleanField(_("Free shipping"), blank=True, null=True,
        help_text=_("Should this discount remove all shipping costs?"))
    includeShipping = models.BooleanField(_("Include shipping"), blank=True, null=True,
        help_text=_("Should shipping be included in the discount calculation?"))
    validProducts = models.ManyToManyField(Product, verbose_name=_("Valid Products"),
        blank=True, null=True, help_text="Make sure not to include gift certificates!")

    def __init__(self, *args, **kwargs):
        self._calculated = False
        super(Discount, self).__init__(*args, **kwargs)

    def __unicode__(self):
        return self.description

    def isValid(self, cart=None):
        """
        Make sure this discount still has available uses and is in the current date range.
        If a cart has been populated, validate that it does apply to the products we have selected.
        """
        if not self.active:
            return (False, ugettext('This coupon is disabled.'))
        if self.startDate > datetime.date.today():
            return (False, ugettext('This coupon is not active yet.'))
        if self.endDate < datetime.date.today():
            return (False, ugettext('This coupon has expired.'))
        if self.numUses > self.allowedUses:
            return (False, ugettext('This discount has exceeded the number of allowed uses.'))
        if not cart:
            return (True, ugettext('Valid.'))

        minOrder = self.minOrder or 0
        if cart.total < minOrder:
            return (False, ugettext('This discount only applies to orders of at least %s.' % moneyfmt(minOrder)))

        validItems = False
        if self.validProducts.count() == 0:
            validItems = True
        else:
            validItems = len(self._valid_cart_products(cart))

        if validItems:
            return (True, ugettext('Valid.'))
        else:
            return (False, ugettext('This discount cannot be applied to the products in your cart.'))

    def _valid_cart_products(self, cart):
        validslugs = self.validProducts.values_list('slug', flat=True)
        cartslugs = cart.cartitem_set.values_list('product__slug', flat=True)
        return ProductPriceLookup.objects.filter(
            discountable=True,
            productslug__in=validslugs, 
            productslug__in=cartslugs
            ).values_list('productslug', flat=True)

    def calc(self, order):
        # Use the order details and the discount specifics to calculate the actual discount
        discounted = {}
        if self.validProducts.count() == 0:
            allvalid = True
        else:
            validproducts = self._valid_cart_products(cart)

        for lineitem in order.orderitem_set.all():
            lid = lineitem.id
            price = lineitem.line_item_price
            if lineitem.product.is_discountable and (allvalid or lineitem.product.slug in validproducts):
                discounted[lid] = price 

        if self.includeShipping and not self.freeShipping:
            shipcost = order.shipping_cost
            discounted['Shipping'] = shipcost

        if self.amount:
            # perform a flat rate discount, applying evenly to all items
            # in cart
            discounted = apply_even_split(discounted, self.amount)

        elif self.percentage:
            discounted = apply_percentage(discounted, self.percentage)

        else:
            # no discount, probably shipping-only
            zero = Decimal("0.00")
            for key in discounted.keys():
                discounted[key] = zero

        if self.freeShipping:
            shipcost = order.shipping_cost
            discounted['Shipping'] = shipcost

        self._item_discounts = discounted
        self._calculated = True

    def _total(self):
        assert(self._calculated)
        return reduce(operator.add, self.item_discounts.values())
    total = property(_total)

    def _item_discounts(self):
        """Get the dictionary of orderitem -> discounts."""
        assert(self._calculated)
        return self._item_discounts
    item_discounts = property(_item_discounts)

    def _percentage_text(self):
        """Get the human readable form of the sale percentage."""
        if self.percentage > 1:
            pct = self.percentage
        else:
            pct = self.percentage*100
        cents = Decimal("0")
        pct = pct.quantize(cents)
        return "%i%%" % pct

    percentage_text = property(_percentage_text)

    def valid_for_product(self, product):
        """Tests if discount is valid for a single product"""
        if not product.is_discountable:
            return False
        p = self.validProducts.filter(id__exact = product.id)
        return p.count() > 0

    class Meta:
        verbose_name = _("Discount")
        verbose_name_plural = _("Discounts")

def apply_even_split(discounted, amount):
    log.debug('Apply even split on %s to: %s', amount, discounted)
    lastct = -1
    ct = len(discounted)
    split_discount = amount/ct

    while ct > 0:
        log.debug("Trying with ct=%i", ct)
        delta = Decimal("0.00")
        applied = Decimal("0.00")
        work = {}
        for lid, price in discounted.items():
            if price > split_discount:
                work[lid] = split_discount
                applied += split_discount
            else:
                work[lid] = price
                delta += price
                applied += price
                ct -= 1

        if applied >= amount - Decimal("0.01"):
            ct = 0

        if ct == lastct:
            ct = 0
        else:
            lastct = ct

        if ct > 0:
            split_discount = (amount-delta)/ct

    round_cents(work)
    return work

def apply_percentage(discounted, percentage):
    work = {}
    if percentage > 1:
        log.warn("Correcting discount percentage, should be less than 1, is %s", percentage)
        percentage = percentage/100

    for lid, price in discounted.items():
        work[lid] = price * percentage
    round_cents(work)
    return work

def round_cents(work):
    cents = Decimal("0.01")
    for lid in work:
        work[lid] = work[lid].quantize(cents)
