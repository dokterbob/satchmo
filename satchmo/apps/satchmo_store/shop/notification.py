from decimal import Decimal
from django.utils.translation import ugettext as _
from livesettings import config_value
from product.models import Discount
from satchmo_store.mail import NoRecipientsException, send_store_mail
import logging

log = logging.getLogger('contact.notifications')

def order_success_listener(order=None, **kwargs):
    """Listen for order_success signal, and send confirmations"""
    if order:
        send_order_confirmation(order)
        send_order_notice(order)

def notify_on_ship_listener(sender, oldstatus="", newstatus="", order=None, **kwargs):
    """Listen for a transition to 'shipped', and notify customer."""

    if oldstatus != 'Shipped' and newstatus == 'Shipped':
        if order.is_shippable:
            send_ship_notice(order)

def send_order_confirmation(order, template='shop/email/order_complete.txt'):
    """Send an order confirmation mail to the customer.
    """

    try:
        sale = Discount.objects.by_code(order.discount_code, raises=True)
    except Discount.DoesNotExist:
        sale = None

    c = {'order': order, 'sale' : sale}
    subject = _("Thank you for your order from %(shop_name)s")

    send_store_mail(subject, c, template, [order.contact.email],
                    format_subject=True)

def send_order_notice(order, template='shop/email/order_placed_notice.txt'):
    """Send an order confirmation mail to the owner.
    """

    if config_value("PAYMENT", "ORDER_EMAIL_OWNER"):
        try:
            sale = Discount.objects.by_code(order.discount_code, raises=True)
        except Discount.DoesNotExist:
            sale = None

        c = {'order': order, 'sale' : sale}
        subject = _("New order on %(shop_name)s")

        eddresses = []
        more = config_value("PAYMENT", "ORDER_EMAIL_EXTRA")
        if more:
            more = [m.strip() for m in more.split(',')]
            for m in more:
                if not m in eddresses:
                    eddresses.append(m)

        eddresses = [e for e in eddresses if e]

        try:
            send_mail(subject, c, template, eddresses, format_subject=True,
                      send_to_store=True)
        except NoRecipientsException:
            log.warn("No shop owner email specified, skipping owner_email")
            return

def send_ship_notice(order, template='shop/email/order_shipped.txt'):
    """Send an order shipped mail to the customer.
    """

    log.debug('ship notice on %s', order)

    c = {'order': order}
    subject = _("Your order from %(shop_name)s has shipped")

    send_mail(subject, c, template, format_subject=True,
              send_to_store=True)
