"""Modifies the calculations of prices to count all items in the cart when figuring quantity discounts.

To activate, simply import in your settings file.
"""

from satchmo_store.shop.signals import satchmo_cartitem_price_query
import logging
log = logging.getLogger('satchmo_ext.contrib.cartqty_discounts')

def lineitem_cartqty_price(cartitem=None, **kwargs):
    cart = cartitem.cart
    qty = cart.numItems
    oldprice = cartitem.qty_price
    newprice = cartitem.get_qty_price(qty)
    if oldprice != newprice:
        cartitem.qty_price = newprice
        log.debug("updated price for item based on cart qty=%i new price on %s = %0.2f", 
            qty, cartitem.product.slug, cartitem.qty_price)

satchmo_cartitem_price_query.connect(lineitem_cartqty_price, sender=None)
log.debug('registered lineitem_cartqty_price')