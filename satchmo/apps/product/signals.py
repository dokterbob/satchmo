"""Satchmo product signals
"""

import django.dispatch

#: Listeners should modify the "success" dictionary to veto the discount validity.
#discount_validate.send(sender=Discount, discount=self, cart=cart,
#contact=contact, shipping_choices=shipping_choices, shipping=shipping, success=success)
discount_validate = django.dispatch.Signal()

#: Listeners should modify the "discounted" dictionary to change the set of discounted cart
#: items.
#discount_filter_items.send(sender=self, discounted=discounted, order=order)
discount_filter_items = django.dispatch.Signal()

#index_prerender.send(Sender, request=request, context=ctx, object_list=somelist)
index_prerender = django.dispatch.Signal()

#satchmo_price_query.send(self, adjustment=PriceAdjustmentCalc)
satchmo_price_query = django.dispatch.Signal()
subtype_order_success = django.dispatch.Signal()
