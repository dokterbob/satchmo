"""Signals sent by the Cart system

Signals:

 - `order_success`: sent when the balance goes to zero during a save.
 - `satchmo_cart_add_complete`: sent when an item has been added to the cart.
 - `satchmo_cart_changed`: sent whenever the cart changes.
 - `satchmo_cartitem_price_query`: sent by the pricing system to allow price
    overrides when displaying line item prices.
"""
import django.dispatch

order_success = django.dispatch.Signal()

#satchmo_cart_add_complete.send(cart, cart=cart, product=product, form=form, request=request)
satchmo_cart_add_complete=django.dispatch.Signal()

satchmo_cart_changed=django.dispatch.Signal()

#satchmo_cartitem_price_query.send(cartitem, cartitem=cartitem)
satchmo_cartitem_price_query=django.dispatch.Signal()

