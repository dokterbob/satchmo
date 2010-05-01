from django.conf import settings
from django.template import loader, Context, TemplateDoesNotExist
from livesettings import config_value
from satchmo_store.shop.signals import rendering_store_mail, sending_store_mail

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

class ShouldNotSendMail(Exception):
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

def send_html_email(sender, send_mail_args=None, context=None, template_html=None ,**kwargs):
    send_html = config_value('SHOP', 'HTML_EMAIL')

    if not send_html:
        return

    # perhaps send_store_mail() was not passed the *template_html* argument
    if not template_html:
        return

    if settings.DEBUG:
        log.info("Attempting to send html mail.")
    try:
        t = loader.get_template(template_html)
        html_body = t.render(context)
    except TemplateDoesNotExist:
        log.warn('Unable to find html email template %s. Falling back to text only email.' % template_html)
        return

    # just like send_store_mail() does
    if not send_mail_args.get('recipient_list'):
        raise NoRecipientsException

    # prepare kwargs for EmailMultiAlternatives()
    fail_silently = send_mail_args.pop('fail_silently')
    send_mail_args['body'] = send_mail_args.pop('message') # the plain text part
    send_mail_args['to'] = send_mail_args.pop('recipient_list')

    msg = EmailMultiAlternatives(**send_mail_args)
    msg.attach_alternative(html_body, "text/html")

    # don't have to handle any errors, as send_store_mail() does so for us.
    msg.send(fail_silently=fail_silently)

    # tell send_store_mail() to abort sending plain text mail
    raise ShouldNotSendMail

def send_store_mail(subject, context, template='', recipients_list=None,
                    format_subject=False, send_to_store=False,
                    fail_silently=False, sender=None, **kwargs):
    """
    :param subject: A string.

    :param format_subject: Determines whether the *subject* parameter is
      formatted. Only the %(shop_name)s specifier is supported now.

    :param context: A dictionary to use when rendering the message body. This
      overwrites an internal dictionary with a single entry, `shop_name`.

    :param template: The path of the plain text template to use when rendering
      the message body.

    :param `**kwargs`: Additional arguments that are passed to listeners of the
      signal :data:`satchmo_store.shop.signals.sending_store_mail`.
    """
    from satchmo_store.shop.models import Config

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

    recipients = recipients_list or []

    if send_to_store:
        recipients.append(shop_email)

    # match send_mail's signature
    send_mail_args = {
        'subject': subject,
        'from_email': shop_email,
        'recipient_list': recipients,
        'fail_silently': fail_silently,
    }

    # let listeners modify context
    rendering_store_mail.send(sender, send_mail_args=send_mail_args, context=c,
                              **kwargs)

    # render text email, regardless of whether html email is used.
    t = loader.get_template(template)
    body = t.render(c)

    # listeners may have set this entry
    if not 'message' in send_mail_args:
        send_mail_args['message'] = body

    try:
        # We inform listeners before checking recipients list, as they may
        # modify it.
        # Listeners may also choose to send mail themselves, so we place this
        # call in the SocketError try block to handle errors for them.
        try:
            sending_store_mail.send(sender, send_mail_args=send_mail_args, \
                                    context=c, **kwargs)
        except ShouldNotSendMail:
            return

        if not recipients:
            raise NoRecipientsException

        send_mail(**send_mail_args)
    except SocketError, e:
        if settings.DEBUG:
            log.error('Error sending mail: %s' % e)
            log.warn("""Ignoring email error, since you are running in DEBUG mode.  Email was:
To: %s
Subject: %s
---
%s""" % (",".join(send_mail_args['recipient_list']), send_mail_args['subject'], send_mail_args['message']))
        else:
            log.fatal('Error sending mail: %s' % e)
            raise IOError('Could not send email. Please make sure your email settings are correct and that you are not being blocked by your ISP.')
