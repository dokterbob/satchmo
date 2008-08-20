"""Sends mail related to accounts."""

from django.conf import settings
from django.core.mail import send_mail
from django.template import Context
from django.template import loader
from django.utils.translation import ugettext
from satchmo.shop.models import Config
from socket import error as SocketError
import logging

log = logging.getLogger('satchmo.accounts.mail')

def send_welcome_email(email, first_name, last_name):
    """Send a store new account welcome mail to `email`."""
    
    t = loader.get_template('registration/welcome.txt')
    shop_config = Config.objects.get_current()
    shop_email = shop_config.store_email
    subject = ugettext("Welcome to %s") % shop_config.store_name
    c = Context({
        'first_name': first_name,
        'last_name': last_name,
        'company_name': shop_config.store_name,
        'site_url': shop_config.site.domain,
        'login_url': settings.LOGIN_URL,
    })
    body = t.render(c)
    try:
        send_mail(subject, body, shop_email, [email], fail_silently=False)
    except SocketError, e:
        if settings.DEBUG:
            log.error('Error sending mail: %s' % e)
            log.warn('Ignoring email error, since you are running in DEBUG mode.  Email was:\nTo:%s\nSubject: %s\n---\n%s', email, subject, body)
        else:
            log.fatal('Error sending mail: %s' % e)
            raise IOError('Could not send email, please check to make sure your email settings are correct, and that you are not being blocked by your ISP.')
