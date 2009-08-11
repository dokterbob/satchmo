"""
This dummy module can be used as a basis for creating your own

- Copy this module to a new name
- Make the changes described below
"""

# Note, make sure you use decimal math everywhere!
from decimal import Decimal
from django.utils.translation import ugettext as _
from shipping.modules.base import BaseShipper

class Shipper(BaseShipper):

    flatRateFee = Decimal("15.00")
    id = "Dumy"
        
    def __str__(self):
        """
        This is mainly helpful for debugging purposes
        """
        return "Dummy Flat Rate"
        
    def description(self):
        """
        A basic description that will be displayed to the user when selecting their shipping options
        """
        return _("Dummy Flat Rate Shipping")

    def cost(self):
        """
        Complex calculations can be done here as long as the return value is a decimal figure
        """
        assert(self._calculated)
        return(self.flatRateFee)

    def method(self):
        """
        Describes the actual delivery service (Mail, FedEx, DHL, UPS, etc)
        """
        return _("US Mail")

    def expectedDelivery(self):
        """
        Can be a plain string or complex calcuation returning an actual date
        """
        return _("3 - 4 business days")

    def valid(self, order=None):
        """
        Can do complex validation about whether or not this option is valid.
        For example, may check to see if the recipient is in an allowed country
        or location.
        """
        return True

