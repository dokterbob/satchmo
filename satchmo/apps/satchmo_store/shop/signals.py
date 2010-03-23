"""Signals sent by the Cart system

Signals:
"""
import django.dispatch

#: Sent when the balance goes to zero during a save.
order_success = django.dispatch.Signal()

#: Sent to check if an order can be cancelled.
order_cancel_query = django.dispatch.Signal()

#: Sent when order is cancelled (e.g. payment gateway cancels payment)
order_cancelled = django.dispatch.Signal()

#satchmo_cart_add_complete.send(cart, cart=cart, cartitem=cartitem, form=form, request=request)
satchmo_cart_add_complete=django.dispatch.Signal()

#satchmo_cart_add_verify(cart, cart=cart, cartitem=cartitem, added_quantity=Decimal('0'), details=details)
satchmo_cart_add_verify=django.dispatch.Signal()

#: Sent whenever the cart changes.
satchmo_cart_changed=django.dispatch.Signal()

#: Sent by the pricing system to allow price overrides when displaying line item
#: prices.
#satchmo_cartitem_price_query.send(cartitem, cartitem=cartitem)
satchmo_cartitem_price_query=django.dispatch.Signal()

#satchmo_cart_details_query.send(cart, product=product, quantity=quantity, details=details, request=request, formdata=formdata)
satchmo_cart_details_query=django.dispatch.Signal()

#: Sent by the order when its status has changed.
#satchmo_order_status_changed.send(self.order, oldstatus=oldstatus, newstatus=status, order=order)
satchmo_order_status_changed=django.dispatch.Signal()

#satchmo_post_copy_item_to_order.send(cart, cartitem=cartitem, order=order, orderitem=orderitem)
satchmo_post_copy_item_to_order=django.dispatch.Signal()

#: Sent by context_processor to optionally add more to the store context.
satchmo_context = django.dispatch.Signal()

#: Sent by 'views.smart_add` to allow listeners to optionally change the
#: responding function.
cart_add_view = django.dispatch.Signal()

#: Sent by the order during the calculation of the total.
#satchmo_shipping_price_query.send(order, adjustment=shipadjust)
satchmo_shipping_price_query = django.dispatch.Signal()
