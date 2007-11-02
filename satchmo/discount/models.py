"""
Sets up a discount that can be applied to a product
"""

from datetime import date
from django.db import models
from django.utils.translation import ugettext, ugettext_lazy as _
from satchmo.product.models import Product
from satchmo.shop.templatetags.satchmo_currency import moneyfmt
from satchmo.shop.utils.validators import MutuallyExclusiveWithField

percentage_validator = MutuallyExclusiveWithField('amount')
amount_validator = MutuallyExclusiveWithField('percentage')

class Discount(models.Model):
    """
    Allows for multiple types of discounts including % and dollar off.
    Also allows finite number of uses.
    """
    description = models.CharField(_("Description"), max_length=100)
    code = models.CharField(_("Discount Code"), max_length=20, unique=True,
        help_text=_("Coupon Code"))
    amount = models.DecimalField(_("Discount Amount"), decimal_places=2,
        max_digits=4, blank=True, null=True, validator_list=[amount_validator],
        help_text=_("Enter absolute discount amount OR percentage."))
    percentage = models.DecimalField(_("Discount Percentage"), decimal_places=2,
        max_digits=4, blank=True, null=True,
        validator_list=[percentage_validator],
        help_text=_("Enter absolute discount amount OR percentage.  Percentage example: \"0.10\"."))
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
    validProducts = models.ManyToManyField(Product, verbose_name=_("Valid Products"), filter_interface=True, blank=True, null=True)

    def __unicode__(self):
        return self.description

    def isValid(self, cart=None):
        """
        Make sure this discount still has available uses and is in the current date range.
        If a cart has been populated, validate that it does apply to the products we have selected.
        """
        if not self.active:
            return (False, ugettext('This coupon is disabled.'))
        if self.startDate > date.today():
            return (False, ugettext('This coupon is not active yet.'))
        if self.endDate < date.today():
            return (False, ugettext('This coupon has expired.'))
        if self.numUses > self.allowedUses:
            return (False, ugettext('This discount has exceeded the number of allowed uses.'))
        if not cart:
            return (True, ugettext('Valid.'))

        minOrder = self.minOrder or 0
        if cart.total < minOrder:
            return (False, ugettext('This discount only applies to orders of at least %s.' % moneyfmt(minOrder)))

        #Check to see if the cart items are included
        validProducts = self.validProducts.all()
        # Skip validProducts check if validProducts is empty
        validItems = not bool(validProducts)
        if validProducts:
            for cart_item in cart.cartitem_set.all():
                if cart_item.product in validProducts:
                    validItems = True
                    break   #Once we have 1 valid item, we exit
        if validItems:
            return (True, ugettext('Valid.'))
        else:
            return (False, ugettext('This discount cannot be applied to the products in your cart.'))

    def calc(self, order):
        # Use the order details and the discount specifics to calculate the actual discount
        if self.amount:
            return(self.amount)
        if self.percentage and self.includeShipping:
            return(self.percentage * (order.sub_total + order.shipping_cost))
        if self.percentage:
            return((self.percentage * order.sub_total))

    class Admin:
        list_display=('description','active')

    class Meta:
        verbose_name = _("Discount")
        verbose_name_plural = _("Discounts")

