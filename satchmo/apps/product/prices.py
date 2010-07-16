from decimal import Decimal
from l10n.utils import moneyfmt
import datetime

def get_product_quantity_adjustments(product, qty=1, parent=None):
    """Gets a list of adjustments for the price found for a product/qty"""

    qty_discounts = product.price_set.exclude(
        expires__isnull=False,
        expires__lt=datetime.date.today()).filter(quantity__lte=qty)

    # Get the price with the quantity closest to the one specified without going over
    adjustments = qty_discounts.order_by('price','-quantity', 'expires')[:1]
    if adjustments:
        adjustments = adjustments[0].adjustments(product)
    else:
        adjustments = None  
        if parent:
            adjustments = get_product_quantity_adjustments(parent, qty=qty)


    if not adjustments:
        adjustments = PriceAdjustmentCalc(None)

    return adjustments

def get_product_quantity_price(product, qty=Decimal('1'), delta=Decimal("0.00"), parent=None):
    """
    Returns price as a Decimal else None.
    First checks the product, if none, then checks the parent.
    """

    adjustments = get_product_quantity_adjustments(product, qty=qty, parent=parent)

    return adjustments.final_price()+delta

# -------------------------------------------
# helper objects - not Django model objects

class PriceAdjustmentCalc(object):
    """Helper class to handle adding up product pricing adjustments"""

    def __init__(self, price, product=None):
        self.price = price
        self.base_product = product
        self.adjustments = []

    def __add__(self, adjustment):
        self.adjustments.append(adjustment)
        return self

    def total_adjustment(self):
        total = Decimal(0)
        for adj in self.adjustments:
            total += adj.amount
        return total

    def _product(self):
        """Lazy product dereference"""
        if self.base_product:
            product = self.base_product
        else:
            product = self.price.product
        return product

    product = property(fget=_product)

    def final_price(self):
        total = Decimal(0)
        if self.price:
            total = self.price.price
            if total is None:
                total = Decimal(0)
        return total - self.total_adjustment()

class PriceAdjustment(object):
    """A single product pricing adjustment"""

    def __init__(self, key, label=None, amount=None):
        if label is None:
            label = key.capitalize()
        if amount is None:
            amount = Decimal(0)
        self.key = key
        self.label = label
        self.amount = amount

    def __unicode__(self):
        return u"%s: %s=%s" % (_('Price Adjustment'), self.label, moneyfmt(self.amount))

