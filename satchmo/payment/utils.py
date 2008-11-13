try:
    from decimal import Decimal
except:
    from django.utils._decimal import Decimal

from datetime import datetime, timedelta
from satchmo.shipping.utils import update_shipping
from satchmo.shop.models import Order, OrderItem, OrderItemDetail, OrderPayment
from satchmo.shop.signals import satchmo_post_copy_item_to_order
from socket import error as SocketError
import logging

log = logging.getLogger('payment.utils')

NOTSET = object()

def create_pending_payment(order, config, amount=NOTSET):
    """Create a placeholder payment entry for the order.  
    This is done by step 2 of the payment process."""
    key = unicode(config.KEY.value)
    if amount == NOTSET:
        amount = Decimal("0.00")

    # kill old pending payments
    payments = order.payments.filter(transaction_id__exact="PENDING", 
        payment__exact=key)
    ct = payments.count()
    if ct > 0:
        log.debug("Deleting %i expired pending payment entries for order #%i", ct, order.id)

        for pending in payments:
            pending.delete()
        
    log.debug("Creating pending %s payment for %s", key, order)

    orderpayment = OrderPayment(order=order, amount=amount, payment=key, 
        transaction_id="PENDING")
    orderpayment.save()

    return orderpayment


def get_or_create_order(request, working_cart, contact, data):
    """Get the existing order from the session, else create using 
    the working_cart, contact and data"""
    shipping = data['shipping']
    discount = data['discount']
    
    try:
        newOrder = Order.objects.from_request(request)
        pay_ship_save(newOrder, working_cart, contact,
            shipping=shipping, discount=discount, update=True)
        
    except Order.DoesNotExist:
        # Create a new order.
        newOrder = Order(contact=contact)
        pay_ship_save(newOrder, working_cart, contact,
            shipping=shipping, discount=discount)
            
        request.session['orderID'] = newOrder.id
    
    return newOrder


def pay_ship_save(new_order, cart, contact, shipping, discount, update=False):
    """Save the order details, first removing all items if this is an update.
    """
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


def record_payment(order, config, amount=NOTSET, transaction_id=""):
    """Convert a pending payment into a real payment."""
    key = unicode(config.KEY.value)
    if amount == NOTSET:
        amount = order.balance
        
    log.debug("Recording %s payment of %s for %s", key, amount, order)
    payments = order.payments.filter(transaction_id__exact="PENDING", 
        payment__exact=key)
    ct = payments.count()
    if ct == 0:
        log.debug("No pending %s payments for %s", key, order)
        orderpayment = OrderPayment(order=order, amount=amount, payment=key,
            transaction_id=transaction_id)
    
    else:
        orderpayment = payments[0]
        orderpayment.amount = amount
        orderpayment.transaction_id = transaction_id

        if ct > 1:
            for payment in payments[1:len(payments)]:
                payment.transaction_id="ABORTED"
                payment.save()
            
    orderpayment.time_stamp = datetime.now()
    orderpayment.save()
    
    if order.paid_in_full:
        order.order_success()
    
    return orderpayment


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
