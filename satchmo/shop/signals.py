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

#satchmo_cart_add_complete.send(cart, cart=cart, cartitem=cartitem, form=form, request=request)
satchmo_cart_add_complete=django.dispatch.Signal()

#satchmo_cart_add_verify(cart, cart=cart, cartitem=cartitem, added_quantity=0, details=details)
satchmo_cart_add_verify=django.dispatch.Signal()

satchmo_cart_changed=django.dispatch.Signal()

#satchmo_cartitem_price_query.send(cartitem, cartitem=cartitem)
satchmo_cartitem_price_query=django.dispatch.Signal()

#satchmo_cart_details_query.send(cart, product=product, quantity=quantity, details=details, request=request, formdata=formdata)
satchmo_cart_details_query=django.dispatch.Signal()

#satchmo_post_copy_item_to_order.send(cart, cartitem=cartitem, order=order, orderitem=orderitem)
satchmo_post_copy_item_to_order=django.dispatch.Signal()
