from django import template
from satchmo_store.shop import get_satchmo_setting
from satchmo_store.shop.models import Order, ORDER_STATUS
from satchmo_store.shop.utils import is_multihost_enabled

register = template.Library()

def customorder_management(order):
    custom = []
    for orderitem in order.orderitem_set.all():
        if 'CustomProduct' in orderitem.product.get_subtypes():
            custom.append(orderitem)

    return {
        'SHOP_BASE' : get_satchmo_setting('SHOP_BASE'),
        'customitems' : custom
    }

register.inclusion_tag('shop/admin/_customorder_management.html')(customorder_management)

def inprocess_order_list():
    """Returns a formatted list of in-process orders"""
    inprocess = unicode(ORDER_STATUS[2][0])
    orders = orders_at_status(inprocess)

    return {
        'orders' : orders,
        'multihost' : is_multihost_enabled()
    }

register.inclusion_tag('shop/admin/_ordercount_list.html')(inprocess_order_list)

def orders_at_status(status):
    return Order.objects.filter(status=status).order_by('-time_stamp')

def orderpayment_list(order):
    return {
        'SHOP_BASE' : get_satchmo_setting('SHOP_BASE'),
        'order' : order,
        'payments' : order.payments.all()
        }

register.inclusion_tag('shop/admin/_orderpayment_list.html')(orderpayment_list)

def pending_order_list():
    """Returns a formatted list of pending orders"""
    pending = unicode(ORDER_STATUS[1][0])
    orders = orders_at_status(pending)

    return {
        'orders' : orders,
        'multihost' : is_multihost_enabled()
    }

register.inclusion_tag('shop/admin/_ordercount_list.html')(pending_order_list)
