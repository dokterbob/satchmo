try:
    from decimal import Decimal
except:
    from django.utils._decimal import Decimal

import logging
from socket import error as SocketError
from django.conf import settings
from django.core.mail import EmailMessage
from django.template import loader, Context
from django.utils.translation import ugettext as _
from satchmo.configuration import config_value

log = logging.getLogger('contact.notifications')

def order_success_listener(sender=None, instance=None):
    """Listen for order_success signal, and send confirmations"""
    send_order_confirmation(instance)
    send_order_notice(instance)

def send_order_confirmation(new_order, template='email/order_complete.txt'):
    """Send an order confirmation mail to the customer.
    """
    from satchmo.shop.models import Config

    shop_config = Config.get_shop_config()
    shop_email = shop_config.store_email
    shop_name = shop_config.store_name
    t = loader.get_template(template)
    c = Context({'order': new_order, 'shop_name': shop_name})
    subject = _("Thank you for your order from %(shop_name)s") % {'shop_name' : shop_name}

    try:
        customer_email = new_order.contact.email
        body = t.render(c)
        message = EmailMessage(subject, body, shop_email, [customer_email])
        message.send()

    except SocketError, e:
        if settings.DEBUG:
            log.error('Error sending mail: %s' % e)
            log.warn('Ignoring email error, since you are running in DEBUG mode.  Email was:\nTo:%s\nSubject: %s\n---\n%s', customer_email, subject, body)
        else:
            log.fatal('Error sending mail: %s' % e)
            raise IOError('Could not send email, please check to make sure your email settings are correct, and that you are not being blocked by your ISP.')
            
def send_order_notice(new_order, template='email/order_placed_notice.txt'):
    """Send an order confirmation mail to the owner.
    """
    from satchmo.shop.models import Config
    
    if config_value("PAYMENT", "ORDER_EMAIL_OWNER"):
        shop_config = Config.get_shop_config()
        shop_email = shop_config.store_email
        shop_name = shop_config.store_name
        t = loader.get_template(template)
        c = Context({'order': new_order, 'shop_name': shop_name})
        subject = _("New order on %(shop_name)s") % {'shop_name' : shop_name}
        
        eddresses = [shop_email, ]
        more = config_value("PAYMENT", "ORDER_EMAIL_EXTRA")
        if more:
            more = [m.strip() for m in more.split(',')]
            for m in more:
                if not m in eddresses:
                    eddresses.append(m)
                    
        eddresses = [e for e in eddresses if e]
        if not eddresses:
            log.warn("No shop owner email specified, skipping owner_email")
            return

        try:
            body = t.render(c)
            message = EmailMessage(subject, body, shop_email, eddresses)
            message.send()

        except SocketError, e:
            if settings.DEBUG:
                log.error('Error sending mail: %s' % e)
                log.warn('Ignoring email error, since you are running in DEBUG mode.  Email was:\nTo:%s\nSubject: %s\n---\n%s', ",".join(eddresses), subject, body)
            else:
                log.fatal('Error sending mail: %s' % e)
                raise IOError('Could not send email, please check to make sure your email settings are correct, and that you are not being blocked by your ISP.')

