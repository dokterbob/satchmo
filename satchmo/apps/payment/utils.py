from datetime import datetime, timedelta
from decimal import Decimal
from livesettings import config_get_group
from payment import active_gateways
from satchmo_store.shop.models import Order, OrderAuthorization, OrderItem, OrderItemDetail, OrderPayment, OrderPendingPayment
from satchmo_store.shop.signals import satchmo_post_copy_item_to_order
from shipping.utils import update_shipping
from socket import error as SocketError
import logging

log = logging.getLogger('payment.utils')

def capture_authorizations(order):
    """Capture all outstanding authorizations on this order"""
    if order.authorized_remaining > Decimal('0'):
        purchase = order.get_or_create_purchase()
        for key, group in active_gateways():
            gateway_settings = config_get(group, 'MODULE')
            processor = get_gateway_by_settings(gateway_settings)
            processor.capture_authorized_payments(purchase)

def get_or_create_order(request, working_cart, contact, data):
    """Get the existing order from the session, else create using 
    the working_cart, contact and data"""
    shipping = data.get('shipping', None)
    discount = data.get('discount', None)
    
    try:
        order = Order.objects.from_request(request)
        if order.status != '':
            # This order is being processed. We should not touch it!
            order = None
    except Order.DoesNotExist:
        order = None

    update = bool(order)
    if order:
        # make sure to copy/update addresses - they may have changed
        order.copy_addresses() 
        order.save()
        if discount is None and order.discount_code:
            discount = order.discount_code
    else:
        # Create a new order.
        order = Order(contact=contact)

    pay_ship_save(order, working_cart, contact,
        shipping=shipping, discount=discount, update=update)
    request.session['orderID'] = order.id
    return order

def get_gateway_by_settings(gateway_settings, settings={}):
    log.debug('getting gateway by settings: %s', gateway_settings.key)
    processor_module = gateway_settings.MODULE.load_module('processor')
    gateway_settings = get_gateway_settings(gateway_settings, settings=settings)
    return processor_module.PaymentProcessor(settings=gateway_settings)

def get_processor_by_key(key):
    payment_module = config_get_group(key)
    processor_module = payment_module.MODULE.load_module('processor')
    return processor_module.PaymentProcessor(payment_module)

def pay_ship_save(new_order, cart, contact, shipping, discount, update=False):
    """
    Save the order details, first removing all items if this is an update.
    """
    if shipping:
        update_shipping(new_order, shipping, contact, cart)

    if not update:
        # Temp setting of the tax and total so we can save it
        new_order.total = Decimal('0.00')
        new_order.tax = Decimal('0.00')
        new_order.sub_total = cart.total
        new_order.method = 'Online'

    if discount:
        new_order.discount_code = discount
    else:
        new_order.discount_code = ""

    update_orderitems(new_order, cart, update=update)

def update_orderitem_details(new_order_item, item):
    """Update orderitem details, if any.
    """
    if item.has_details:
        # Check to see if cartitem has CartItemDetails
        # If so, add here.
        #obj = CustomTextField.objects.get(id=item.details.values()[0]['customfield_id'])
        #val = item.details.values()[0]['detail']
        for detail in item.details.all():
            new_details = OrderItemDetail(item=new_order_item,
                value=detail.value,
                name=detail.name,
                price_change=detail.price_change,
                sort_order=detail.sort_order)
            new_details.save()


def update_orderitem_for_subscription(new_order_item, item):
    """Update orderitem subscription details, if any.
    """
    #if product is recurring, set subscription end
    #if item.product.expire_length:
    if item.product.is_subscription:
        subscription = item.product.subscriptionproduct
        if subscription.expire_length:
            new_order_item.expire_date = subscription.calc_expire_date()
    else:
        subscription = None

    #if product has trial price, set it here and update expire_date with trial period.
    trial = None

    if subscription:
        trial = subscription.get_trial_terms()

    if trial:
        trial1 = trial[0]
        new_order_item.unit_price = trial1.price
        new_order_item.line_item_price = new_order_item.quantity * new_order_item.unit_price
        new_order_item.expire_date = trial1.calc_expire_date()

    new_order_item.save()


def update_orderitems(new_order, cart, update=False):
    """Update the order with all cart items, first removing all items if this
    is an update.
    """
    if update:
        new_order.remove_all_items()
    else:
        # have to save first, or else we can't add orderitems
        new_order.site = cart.site
        new_order.save()

    # Add all the items in the cart to the order
    for item in cart.cartitem_set.all():
        new_order_item = OrderItem(order=new_order,
            product=item.product,
            quantity=item.quantity,
            unit_price=item.unit_price,
            line_item_price=item.line_total)

        update_orderitem_for_subscription(new_order_item, item)
        update_orderitem_details(new_order_item, item)

        # Send a signal after copying items
        # External applications can copy their related objects using this
        satchmo_post_copy_item_to_order.send(
                cart,
                cartitem=item,
                order=new_order, orderitem=new_order_item
                )

    new_order.recalculate_total()
