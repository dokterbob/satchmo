"""
Each shipping option uses the data in an Order object to calculate the shipping cost and return the value
"""
from decimal import Decimal
from django.utils.translation import ugettext, ugettext_lazy
from livesettings import config_value
_ = ugettext_lazy
from shipping.modules.base import BaseShipper

class Shipper(BaseShipper):
    id = "PerItem"

    def __str__(self):
        """
        This is mainly helpful for debugging purposes
        """
        return "Per Item: %s" % config_value('SHIPPING', 'PER_RATE')

    def description(self):
        """
        A basic description that will be displayed to the user when selecting their shipping options
        """
        return _("Per Item shipping")

    def cost(self):
        """
        Complex calculations can be done here as long as the return value is a dollar figure
        """
        fee = Decimal("0.00")
        rate = config_value('SHIPPING', 'PER_RATE')
        for cartitem in self.cart.cartitem_set.all():
            if cartitem.product.is_shippable:
                fee += rate * cartitem.quantity
        return fee

    def method(self):
        """
        Describes the actual delivery service (Mail, FedEx, DHL, UPS, etc)
        """
        return ugettext(config_value('SHIPPING', 'PER_SERVICE'))

    def expectedDelivery(self):
        """
        Can be a plain string or complex calcuation returning an actual date
        """
        return ugettext(config_value('SHIPPING', 'PER_DAYS'))

    def valid(self, order=None):
        """
        Can do complex validation about whether or not this option is valid.
        For example, may check to see if the recipient is in an allowed country
        or location.
        """
        return True

