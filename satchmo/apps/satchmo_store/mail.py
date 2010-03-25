from django.conf import settings
from django.template import loader, Context, TemplateDoesNotExist
from livesettings import config_value

import os.path
from socket import error as SocketError

import logging
log = logging.getLogger('satchmo_store.mail')

if "mailer" in settings.INSTALLED_APPS:
    from mailer import send_mail
else:
    from django.core.mail import send_mail

from django.core.mail import EmailMultiAlternatives

class NoRecipientsException(StandardError):
    pass

def send_store_mail_template_decorator(template_base):
    """
    This decorator sets the arguments ``template`` and ``template_html``
    when the decorated function is called.
    """
    def dec(func):
        def newfunc(*args, **kwargs):
            default_kwargs = {
                'template': '%s.txt' % template_base,
                'template_html': '%s.html' % template_base
            }
            default_kwargs.update(kwargs)
            return func(*args, **default_kwargs)
        return newfunc
    return dec

def send_store_mail(subject, context, template='', recipients_list=None,
                    format_subject=False, send_to_store=False,
                    template_html='', fail_silently=False):
    """
    :parameter: subject: A string.

    :parameter: format_subject: Determines whether the *subject* parameter
     is formatted. Only the %(shop_name)s specifier is supported now.

    :parameter: context: A dictionary to use when rendering the message body.
      This dictionary overwrites an internal dictionary which provides the key
      `shop_name`.

    :parameter: template: The path of the plain text template to use when
      rendering the message body.

    :parameter: template_html: The path of the HTML template to use when
      rendering the message body; this will only be used if the config
      ``SHOP.HTML_EMAIL`` is true.
    """
    from satchmo_store.shop.models import Config

    shop_config = Config.objects.get_current()
    shop_email = shop_config.store_email
    shop_name = shop_config.store_name
    send_html = config_value('SHOP', 'HTML_EMAIL')
    if not shop_email:
        log.warn('No email address configured for the shop.  Using admin settings.')
        shop_email = settings.ADMINS[0][1]

    c_dict = {'shop_name': shop_name}

    if format_subject:
        subject = subject % c_dict

    c_dict.update(context)
    c = Context(c_dict)

    # render text email, regardless of whether html email is used.
    t = loader.get_template(template)
    body = t.render(c)

    if send_html:
        if settings.DEBUG:
            log.info("Attempting to send html mail.")
        try:
            t = loader.get_template(template_html)
            html_body = t.render(c)
        except TemplateDoesNotExist:
            log.warn('Unable to find html email template %s. Falling back to text only email.' % template_html)
            send_html = False

    recipients = recipients_list or []

    if send_to_store:
        recipients.append(shop_email)

    if not recipients:
        raise NoRecipientsException

    try:
        if send_html:
            # email contains both text and html
            msg = EmailMultiAlternatives(subject, body, shop_email, recipients)
            msg.attach_alternative(html_body, "text/html")
            msg.send(fail_silently=fail_silently)
        else:
            send_mail(subject, body, shop_email, recipients,
                      fail_silently=fail_silently)
    except SocketError, e:
        if settings.DEBUG:
            log.error('Error sending mail: %s' % e)
            log.warn('Ignoring email error, since you are running in DEBUG mode.  Email was:\nTo:%s\nSubject: %s\n---\n%s', ",".join(recipients), subject, body)
        else:
            log.fatal('Error sending mail: %s' % e)
            raise IOError('Could not send email. Please make sure your email settings are correct and that you are not being blocked by your ISP.')
