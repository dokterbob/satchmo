"""Modifies the calculations of prices to count all items in the cart when figuring quantity discounts.

To activate, simply import in your settings file.
"""

from django.dispatch import dispatcher
from satchmo.product.signals import satchmo_price_query
from satchmo.shop.signals import satchmo_cartitem_price_query
import logging
log = logging.getLogger('satchmo.contrib.cartqty_discounts')

def lineitem_cartqty_price(cartitem=None):
    cart = cartitem.cart
    qty = cart.numItems
    log.debug("price of cartitem before = %0.2f", cartitem.qty_price)
    cartitem.qty_price = cartitem.get_qty_price(qty)
    log.debug("after calc with cart qty=%i price = %0.2f", qty, cartitem.qty_price)

dispatcher.connect(lineitem_cartqty_price, signal=satchmo_cartitem_price_query)
log.debug('registered lineitem_cartqty_price')