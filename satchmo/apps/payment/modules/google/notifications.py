'''
Created on 3 Mar 2009

@author: dalore
'''
from django.utils.translation import ugettext as _
from livesettings import config_get_group
from payment.utils import get_processor_by_key
from satchmo_store.shop.models import Cart, Order, OrderPayment
import re

def find_order(data):
    """
    Helper function to find order using a google id
    """
    transaction_id = data['google-order-number']
    payment = OrderPayment.objects.filter(transaction_id__exact=transaction_id)[0]
    order = payment.order
    return order

def notify_neworder(request, data):
    """
    Called when google reports a new order.
    
    Looks up the order from the private data and sets the status.
    Empties the cart.
    """
    # get params from data
    private_data = data['shopping-cart.merchant-private-data']
    order_id = re.search('satchmo-order id="(\d+)"', private_data).group(1)
    order = Order.objects.get(pk=order_id)
    payment_module = config_get_group('PAYMENT_GOOGLE')
    processor = get_processor_by_key('PAYMENT_GOOGLE')
    
    # record pending payment
    amount = data['order-total']
    pending_payment = processor.create_pending_payment(order)
    # save transaction id so we can find this order later
    pending_payment.capture.transaction_id = data['google-order-number']
    pending_payment.capture.save()
    
    # delete cart
    for cart in Cart.objects.filter(customer=order.contact):
        cart.empty()
        cart.delete()
        
    # set status
    order.add_status(status='New', notes=_("Received through Google Checkout."))
    
        
def do_charged(request, data):
    """
    Called when google sends a charged status update
    Note that the charged amount comes in a seperate call
    """
    # find order from google id
    order = find_order(data)
    
    # Added to track total sold for each product
    for item in order.orderitem_set.all():
        product = item.product
        product.total_sold += item.quantity
        product.items_in_stock -= item.quantity
        product.save()
        
    # process payment
    processor = get_processor_by_key('PAYMENT_GOOGLE')
    # setting status to billed (why does paypal set it to new?)
    order.add_status(status='Billed', notes=_("Paid through Google Checkout."))
    
def do_shipped(request, data):
    """
    Called when you use the google checkout console to mark order has been shipped
    """
    # find order from google id
    order = find_order(data)
    # process payment
    processor = get_processor_by_key('PAYMENT_GOOGLE')
    # setting status to billed (why does paypal set it to new?)
    order.add_status(status='Shipped', notes=_("Shipped through Google Checkout."))
    

def notify_statechanged(request, data):
    """
    This is called when there has been a change in the order state
    """
    # financial state
    financial_state = data['new-financial-order-state']
    fulfillment_state = data['new-fulfillment-order-state']
    if financial_state == 'CHARGED':
        if fulfillment_state == 'PROCESSING':
            do_charged(request, data)
        elif fulfillment_state == 'DELIVERED':
            do_shipped(request, data)
    
        
def notify_chargeamount(request, data):
    """
    This gets called when google sends a charge amount
    """
    # find order from google id
    order = find_order(data)
    transaction_id = data['google-order-number']
    processor = get_processor_by_key('PAYMENT_GOOGLE')
    processor.record_payment(amount=data['latest-charge-amount'], transaction_id=transaction_id, order=order)

