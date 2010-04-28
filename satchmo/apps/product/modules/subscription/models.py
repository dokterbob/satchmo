from django.db import models
from django.utils.translation import ugettext_lazy as _
from product.models import Product, get_product_quantity_price, get_product_quantity_adjustments
from decimal import Decimal
import datetime
from satchmo_utils import add_month
from satchmo_utils.fields import CurrencyField

SATCHMO_PRODUCT=True

def get_product_types():
    return ('SubscriptionProduct',)

class SubscriptionProduct(models.Model):
    """
    This type of Product is for recurring billing (memberships, subscriptions, payment terms)
    """
    product = models.OneToOneField(Product, verbose_name=_("Product"), primary_key=True)
    recurring = models.BooleanField(_("Recurring Billing"), help_text=_("Customer will be charged the regular product price on a periodic basis."), default=False)
    recurring_times = models.IntegerField(_("Recurring Times"), help_text=_("Number of payments which will occur at the regular rate.  (optional)"), null=True, blank=True)
    expire_length = models.IntegerField(_("Duration"), help_text=_("Length of each billing cycle"), null=True, blank=True)
    SUBSCRIPTION_UNITS = (
        ('DAY', _('Days')),
        ('MONTH', _('Months'))
    )
    expire_unit = models.CharField(_("Expire Unit"), max_length=5, choices=SUBSCRIPTION_UNITS, default="DAY", null=False)
    SHIPPING_CHOICES = (
        ('0', _('No Shipping Charges')),
        ('1', _('Pay Shipping Once')),
        ('2', _('Pay Shipping Each Billing Cycle')),
    )
    is_shippable = models.IntegerField(_("Shippable?"), help_text=_("Is this product shippable?"), max_length=1, choices=SHIPPING_CHOICES)

    is_subscription = True

    def _get_subtype(self):
        return 'SubscriptionProduct'

    def __unicode__(self):
        return self.product.slug

    def _get_fullPrice(self):
        """
        returns price as a Decimal
        """
        return self.get_qty_price(1)

    unit_price = property(_get_fullPrice)

    def get_qty_price(self, qty, show_trial=True, include_discount=True):
        """
        If QTY_DISCOUNT prices are specified, then return the appropriate discount price for
        the specified qty.  Otherwise, return the unit_price
        returns price as a Decimal

        Note: If a subscription has a trial, then we'll return the first trial price, otherwise the checkout won't
        balance and it will look like there are items to be paid on the order.
        """
        if show_trial:
            trial = self.get_trial_terms(0)
        else:
            trial = None

        if trial:
            price = trial.price * qty
        else:
            if include_discount:
                price = get_product_quantity_price(self.product, qty)
            else:
                adjustment = get_product_quantity_adjustments(self, qty)
                if adjustment.price is not None:
                    price = adjustment.price.price
                else:
                    price = None

            if not price and qty == Decimal('1'):      # Prevent a recursive loop.
                price = Decimal("0.00")
            elif not price:
                price = self.product._get_fullPrice()
        return price

    def recurring_price(self):
        """
        Get the non-trial price.
        """
        return self.get_qty_price(Decimal('1'), show_trial=False)

    # use order_success() and DownloadableProduct.create_key() to add user to group and perform other tasks
    def get_trial_terms(self, trial=None):
        """Get the trial terms for this subscription"""
        if trial is None:
            return self.trial_set.all().order_by('id')
        else:
            try:
                return self.trial_set.all().order_by('id')[trial]
            except IndexError:
                return None

    def calc_expire_date(self, date=None):
        if date is None:
            date = datetime.datetime.now()
        if self.expire_unit == "DAY":
            expiredate = date + datetime.timedelta(days=self.expire_length)
        else:
            expiredate = add_month(date, n=self.expire_length)

        return expiredate

    def save(self, **kwargs):
        if hasattr(self.product,'_sub_types'):
            del self.product._sub_types
        super(SubscriptionProduct, self).save(**kwargs)

    class Meta:
        verbose_name = _("Subscription Product")
        verbose_name_plural = _("Subscription Products")

class Trial(models.Model):
    """
    Trial billing terms for subscription products.
    Separating it out lets us have as many trial periods as we want.
    Note that some third party payment processors support only a limited number of trial
    billing periods.  For example, PayPal limits us to 2 trial periods, so if you are using
    PayPal for a billing option, you need to create no more than 2 trial periods for your
    product.  However, gateway based processors like Authorize.net can support as many
    billing periods as you wish.
    """
    subscription = models.ForeignKey(SubscriptionProduct)
    price = CurrencyField(_("Price"), help_text=_("Set to 0 for a free trial.  Leave empty if product does not have a trial."), max_digits=10, decimal_places=2, null=True, )
    expire_length = models.IntegerField(_("Trial Duration"), help_text=_("Length of trial billing cycle.  Leave empty if product does not have a trial."), null=True, blank=True)

    def __unicode__(self):
        return unicode(self.price)

    def _occurrences(self):
        if self.expire_length:
            return int(self.expire_length/self.subscription.expire_length)
        else:
            return 0
    occurrences = property(fget=_occurrences)

    def calc_expire_date(self, date=None):
        if date is None:
            date = datetime.datetime.now()
        if self.subscription.expire_unit == "DAY":
            expiredate = date + datetime.timedelta(days=self.expire_length)
        else:
            expiredate = add_month(date, n=self.expire_length)

        return expiredate

    class Meta:
        ordering = ['-id']
        verbose_name = _("Trial Terms")
        verbose_name_plural = _("Trial Terms")

