"""Sends mail related to accounts."""

from django.conf import settings
from django.utils.translation import ugettext
from satchmo_store.mail import send_store_mail
import logging
from satchmo_store.shop.models import Config


log = logging.getLogger('satchmo_store.accounts.mail')

def send_welcome_email(email, first_name, last_name):
    """Send a store new account welcome mail to `email`."""

    shop_config = Config.objects.get_current()
    subject = ugettext("Welcome to %(shop_name)s")
    c = {
        'first_name': first_name,
        'last_name': last_name,
        'site_url': shop_config.site.domain,
        'login_url': settings.LOGIN_URL,
    }
    send_store_mail(subject, c, 'registration/welcome.txt', [email],
                    format_subject=True)
