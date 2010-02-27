from django.conf import settings
from django.template import loader, Context
from satchmo_store.shop.models import Config
from socket import error as SocketError
import logging

log = logging.getLogger('satchmo_store.mail')

if "mailer" in settings.INSTALLED_APPS:
    from mailer import send_mail
else:
    from django.core.mail import send_mail

class NoRecipientsException(StandardError):
    pass

def send_store_mail(subject, context, template, recipients_list=None,
                    format_subject=False, send_to_store=False,
                    fail_silently=False):
    """
    :parameter: subject: A string.

    :parameter: format_subject: Determines whether the *subject* parameter
     is formatted. Only the %(shop_name)s specifier is supported now.

    :parameter: context: A dictionary to use when rendering the message body.
      This dictionary overwrites an internal dictionary which provides the key
      `shop_name`.

    :parameter: template: The path of the template to use when rendering the
      message body.
    """
    shop_config = Config.objects.get_current()
    shop_email = shop_config.store_email
    shop_name = shop_config.store_name

    if not shop_email:
        log.warn('No email address configured for the shop.  Using admin settings.')
        shop_email = settings.ADMINS[0][1]

    c_dict = {'shop_name': shop_name}

    if format_subject:
        subject = subject % c_dict

    c_dict.update(context)
    c = Context(c_dict)

    t = loader.get_template(template)
    body = t.render(c)

    recipients = recipients_list or []

    if send_to_store:
        recipients.append(shop_email)

    if not recipients:
        raise NoRecipientsException

    try:
        send_mail(subject, body, shop_email, recipients,
                  fail_silently=fail_silently)
    except SocketError, e:
        if settings.DEBUG:
            log.error('Error sending mail: %s' % e)
            log.warn('Ignoring email error, since you are running in DEBUG mode.  Email was:\nTo:%s\nSubject: %s\n---\n%s', ",".join(recipients), subject, message)
        else:
            log.fatal('Error sending mail: %s' % e)
            raise IOError('Could not send email. Please make sure your email settings are correct and that you are not being blocked by your ISP.')
