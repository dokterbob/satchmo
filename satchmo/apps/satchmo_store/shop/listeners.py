from livesettings import config_value
from payment.listeners import capture_on_ship_listener
from product.models import Product
from product.listeners import default_product_search_listener, discount_used_listener
from satchmo_store.contact import signals as contact_signals
from satchmo_store.mail import send_html_email
from satchmo_store.shop import signals
from satchmo_store.shop.exceptions import OutOfStockError
from satchmo_store.shop.models import Order
from signals_ahoy.signals import application_search

import notification
import logging

log = logging.getLogger('shop.listeners')

# --------------- Optional listeners
def only_one_item_in_cart(sender, cart=None, cartitem=None, **kwargs):
    for item in cart.cartitem_set.all():
        if not item == cartitem:
            log.debug('only one item in cart active: removing %s', item)
            item.delete()

# --------------- Default listeners

def decrease_inventory_on_sale(sender, order=None, **kwargs):
    """Track inventory and total sold."""
    # Added to track total sold for each product
    for item in order.orderitem_set.all():
        product = item.product
        product.total_sold += item.quantity
        if config_value('PRODUCT','TRACK_INVENTORY'):
            product.items_in_stock -= item.quantity
        product.save()

def recalc_total_on_contact_change(contact=None, **kwargs):
    """If the contact has changed, recalculate the order total to ensure all current triggers are hit."""
    #TODO: pull just the current order once we start using threadlocal middleware
    log.debug("Recalculating all contact orders not in process")
    orders = Order.objects.filter(contact=contact, status="")
    log.debug("Found %i orders to recalc", orders.count())
    for order in orders:
        order.copy_addresses()
        order.recalculate_total()

def remove_order_on_cart_update(request=None, cart=None, **kwargs):
    """Remove partially completed order when the cart is updated"""
    if request:
        log.debug("caught cart changed signal - remove_order_on_cart_update")
        Order.objects.remove_partial_order(request)

def veto_out_of_stock(sender, cartitem=None, added_quantity=0, **kwargs):
    """Listener which vetoes adding products to the cart which are out of stock."""

    if config_value('PRODUCT','NO_STOCK_CHECKOUT') == False:
        product = cartitem.product
        need_qty = cartitem.quantity + added_quantity
        if product.items_in_stock < need_qty:
            log.debug('out of stock on %s', product.slug)
            raise OutOfStockError(product, product.items_in_stock, need_qty)


def start_default_listening():
    """Add required default listeners"""
    contact_signals.satchmo_contact_location_changed.connect(recalc_total_on_contact_change, sender=None)
    signals.order_success.connect(decrease_inventory_on_sale)
    signals.order_success.connect(notification.order_success_listener, sender=None)
    signals.order_success.connect(discount_used_listener, sender=None)
    signals.satchmo_cart_changed.connect(remove_order_on_cart_update, sender=None)
    application_search.connect(default_product_search_listener, sender=Product)
    signals.satchmo_order_status_changed.connect(capture_on_ship_listener)
    signals.satchmo_order_status_changed.connect(notification.notify_on_ship_listener)
    signals.satchmo_cart_add_verify.connect(veto_out_of_stock)

    signals.sending_store_mail.connect(send_html_email)

    log.debug('Added default shop listeners')
