from decimal import Decimal
from django.conf import settings
from django.core.mail import send_mail
from django.template import loader, Context
from django.utils.translation import ugettext as _
from satchmo.configuration import config_value
from satchmo.contact.models import OrderItem, OrderItemDetail
from satchmo.product.models import CustomTextField
from satchmo.shipping.config import shipping_method_by_key
from satchmo.shop.models import Config
from satchmo.shop.utils import load_module
from socket import error as SocketError
import logging

log = logging.getLogger('pay_ship')

def pay_ship_save(new_order, cart, contact, shipping, discount):
    # Set a default for when no shipping module is used
    new_order.shipping_cost = Decimal("0.00")

    # Save the shipping info
    shipper = shipping_method_by_key(shipping)
    shipper.calculate(cart, contact)
    new_order.shipping_description = shipper.description().encode()
    new_order.shipping_method = shipper.method()
    new_order.shipping_cost = shipper.cost()
    new_order.shipping_model = shipping

    # Temp setting of the tax and total so we can save it
    new_order.total = Decimal('0.00')
    new_order.tax = Decimal('0.00')
    new_order.sub_total = cart.total

    new_order.method = 'Online'
    
    if discount:
        new_order.discount_code = discount
        
    # save so that we can add orderitems
    new_order.save()
    
    # Add all the items in the cart to the order
    for item in cart.cartitem_set.all():
        new_order_item = OrderItem(order=new_order, product=item.product, quantity=item.quantity,
        unit_price=item.unit_price, line_item_price=item.line_total)
        new_order_item.save()
        if item.has_details:
            # Check to see if cartitem has CartItemDetails
            # If so, add here.
            #obj = CustomTextField.objects.get(id=item.details.values()[0]['customfield_id'])
            #val = item.details.values()[0]['detail']
            for detail in item.details.all():
                new_details = OrderItemDetail(item=new_order_item, value=detail.value, name=detail.name, price_change=detail.price_change, sort_order=detail.sort_order)
                new_details.save()
    new_order.recalculate_total()

def send_order_confirmation(newOrder, template='email/order_complete.txt'):
    """Send an order confirmation mail to the customer."""
    shop_config = Config.get_shop_config()
    shop_email = shop_config.store_email
    shop_name = shop_config.store_name
    t = loader.get_template(template)
    c = Context({'order': newOrder,
                  'shop_name': shop_name})
    subject = _("Thank you for your order from %(shop_name)s") % {'shop_name' : shop_name}

    try:
        email = newOrder.contact.email
        body = t.render(c)
        send_mail(subject, body, shop_email,
                  [email], fail_silently=False)
    except SocketError, e:
        if settings.DEBUG:
            log.error('Error sending mail: %s' % e)
            log.warn('Ignoring email error, since you are running in DEBUG mode.  Email was:\nTo:%s\nSubject: %s\n---\n%s', email, subject, body)
        else:
            log.fatal('Error sending mail: %s' % e)
            raise IOError('Could not send email, please check to make sure your email settings are correct, and that you are not being blocked by your ISP.')    
