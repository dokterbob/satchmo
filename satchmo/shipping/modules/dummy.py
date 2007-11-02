"""
This dummy module can be used as a basis for creating your own

- Copy this file to a new name
- Make the changes described below
"""

# Note, make sure you use decimal math everywhere!
from decimal import Decimal
from django.utils.translation import ugettext as _

class Calc(object):
    #Define some constants here
    #The most important is that id is unique
    flatRateFee = Decimal("15.00")
    id = "Dumy"

    def __init__(self, cart, contact):
        # We're copying in the cart and contact info because we'll probably use
        # it later.

        self.cart = cart
        self.contact = contact

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

