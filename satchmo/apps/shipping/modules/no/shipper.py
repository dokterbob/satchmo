"""
Each shipping option uses the data in an Order object to calculate the shipping cost and return the value
"""
from decimal import Decimal
from django.utils.translation import ugettext, ugettext_lazy as _
#from livesettings import config_value
from shipping.modules.base import BaseShipper

class Shipper(BaseShipper):
    id = "NoShipping"

    def __str__(self):
        """
        This is mainly helpful for debugging purposes
        """
        return "No shipping"

    def description(self):
        """
        A basic description that will be displayed to the user when selecting their shipping options
        """
        return _("No Shipping")

    def cost(self):
        """
        Complex calculations can be done here as long as the return value is a dollar figure
        """
        return Decimal("0.00")

    def method(self):
        """
        Describes the actual delivery service (Mail, FedEx, DHL, UPS, etc)
        """
        return ugettext('No Shipping')

    def expectedDelivery(self):
        """
        Can be a plain string or complex calcuation returning an actual date
        """
        return _("immediately")

    def valid(self, order=None):
        """
        Can do complex validation about whether or not this option is valid.
        For example, may check to see if the recipient is in an allowed country
        or location.
        """
        return True

