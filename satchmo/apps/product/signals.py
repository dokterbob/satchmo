"""Satchmo product signals
"""

import django.dispatch

#: Listeners should modify the "success" dictionary to veto the discount validity.
#discount_validate.send(sender=Discount, discount=self, cart=cart,
#contact=contact, shipping_choices=shipping_choices, shipping=shipping, success=success)
discount_validate = django.dispatch.Signal()

#: Sent to verify the set of order items that are subject to discount.
#:
#: Listeners should modify the "discounted" dictionary to change the set of
#: discounted cart items.
#:
#: :param sender: The discount being applied.
#: :type sender: ``product.models.Discount``
#:
#: :param discounted: A dictionary, where the keys are IDs of items which are
#:   subject to discount by standard criteria.
#:
#: :param order: The order being processed.
#: :type order: ``satchmo_store.shop.models.Order``
discount_filter_items = django.dispatch.Signal()

#: Sent before an index is rendered for categories or brands.
#:
#: :param sender: An instance of one of the following models:
#:
#:   - ``product.models.product``
#:   - ``satchmo_ext.brand.models.Brand``
#:   - ``satchmo_ext.brand.models.BrandProduct``
#:
#: :param request: The request used by the view.
#: :type request: ``django.http.HttpRequest``
#:
#: :param context: A dictionary containing the context that will be used to
#:   render the template. The contents of this dictionary changes depending on
#:   the sender.
#:
#: :param category: The category being viewed.
#: :type category: ``product.models.Category``
#:
#: :param brand: The brand being viewed.
#: :type brand: ``satchmo_ext.brand.modes.Brand``
#:
#: :param object_list: A ``QuerySet`` of ``product.models.Product`` objects.
#:
#: .. Note:: *category* and *brand* will not be passed for category listings.
index_prerender = django.dispatch.Signal()

# FIXME document adjustment=PriceAdjustmentCalc

#: Sent before returning the price of a product.
#:
#: :param sender: An instance of one of the following models:
#:
#:  - ``product.models.ProductPriceLookup``
#:  - ``product.models.Price``
#:  - ``satchmo_ext.tieredpricing.models.TieredPrice``
#:
#: :param price: The instance of the model sending the price query.
#:
#: :param slug: The slug of the product being queried
#:
#: :param discountable: A Boolean representing whether or not the product price
#:   is discountable
#:
#: .. Note:: *slug* and *discountable* are only sent by
#:    ``product.models.ProductPriceLookup``.
#: .. Note:: *price* is the same as *sender*
satchmo_price_query = django.dispatch.Signal()

#: Sent when a downloadable product is successful.
#:
#: :param sender: The product that was successfully ordered.
#: :type sender: ``product.models.DownloadableProduct``
#:
#: :param product: The product that was successfully ordered.
#: :type product: ``product.models.DownoadableProduct``
#:
#: :param order: The successful order for the product.
#: :type order: ``satchmo_store.shop.models.Order``
#:
#: :param subtype: Always the string ``"download"``.
subtype_order_success = django.dispatch.Signal()

