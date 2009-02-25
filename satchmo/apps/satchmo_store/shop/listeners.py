from django.conf import settings
from django.utils.translation import ugettext, gettext_lazy as _
from livesettings import config_value
from payment.listeners import capture_on_ship_listener
from product import signals as product_signals
from product.models import Product
from product.listeners import default_product_search_listener
from satchmo_store.contact import signals as contact_signals
from satchmo_store.shop import signals
from satchmo_store.shop.exceptions import OutOfStockError
from satchmo_store.shop.models import DownloadLink, Order

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

def create_download_link(product=None, order=None, subtype=None, **kwargs):
    """Creates a download link for a Downloadable Product on order success."""
    if product and order and subtype == "download":        
        new_link = DownloadLink(downloadable_product=product, order=order, 
            key=product.create_key(), num_attempts=0)
        new_link.save()
        #TODO: fix this so that it only sets shipped if all items were Downloads
        # if not order.status == 'Shipped'
        #     order.add_status('Shipped', ugettext("Order immediately available for download"))
    else:
        log.debug("ignoring subtype_order_success signal, looking for download product, got %s", subtype)

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
    product_signals.subtype_order_success.connect(create_download_link, sender=None)
    contact_signals.satchmo_contact_location_changed.connect(recalc_total_on_contact_change, sender=None)
    signals.order_success.connect(notification.order_success_listener, sender=None)
    signals.satchmo_cart_changed.connect(remove_order_on_cart_update, sender=None)
    signals.satchmo_search.connect(default_product_search_listener, sender=Product)
    signals.satchmo_order_status_changed.connect(capture_on_ship_listener)
    signals.satchmo_order_status_changed.connect(notification.notify_on_ship_listener)
    signals.satchmo_cart_add_verify.connect(veto_out_of_stock)
    log.debug('Added default shop listeners')
