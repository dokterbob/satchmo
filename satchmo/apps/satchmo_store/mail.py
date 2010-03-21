from django.conf import settings
from django.template import loader, Context, TemplateDoesNotExist
from satchmo_store.shop.models import Config
from socket import error as SocketError
import logging
from livesettings import config_value
import os.path

log = logging.getLogger('satchmo_store.mail')

if "mailer" in settings.INSTALLED_APPS:
    from mailer import send_mail
else:
    from django.core.mail import send_mail

from django.core.mail import EmailMultiAlternatives

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

    If store config is set to enable HTML emails, will attempt to find the HTML
    template and send it.
    """
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

    t = loader.get_template(template)
    body = t.render(c)

    if send_html:
        base_dir,base_name = os.path.split(template)
        file_name, ext = os.path.splitext(base_name)
        template_name = file_name + '.html'
        if settings.DEBUG:
            log.info("Attempting to send html mail.")
        try:
            html_t = loader.get_template(os.path.join(base_dir, template_name))
            html_body = html_t.render(c)
        except TemplateDoesNotExist:
            log.warn('Unable to find html email template %s. Falling back to text only email.', os.path.join(base_dir, template_name))
            send_html = False

    recipients = recipients_list or []

    if send_to_store:
        recipients.append(shop_email)

    if not recipients:
        raise NoRecipientsException

    if send_html:
        msg = EmailMultiAlternatives(subject, body, shop_email, recipients)
        msg.attach_alternative(html_body, "text/html")
        try:
            msg.send(fail_silently=fail_silently)
        except SocketError, e:
            if settings.DEBUG:
                log.error('Error sending mail: %s' % e)
                log.warn('Ignoring email error, since you are running in DEBUG mode.  Email was:\nTo:%s\nSubject: %s\n---\n%s', ",".join(recipients), subject, body)
            else:
                log.fatal('Error sending mail: %s' % e)
                raise IOError('Could not send email. Please make sure your email settings are correct and that you are not being blocked by your ISP.')
    else:
        try:
            send_mail(subject, body, shop_email, recipients,
                      fail_silently=fail_silently)
        except SocketError, e:
            if settings.DEBUG:
                log.error('Error sending mail: %s' % e)
                log.warn('Ignoring email error, since you are running in DEBUG mode.  Email was:\nTo:%s\nSubject: %s\n---\n%s', ",".join(recipients), subject, body)
            else:
                log.fatal('Error sending mail: %s' % e)
                raise IOError('Could not send email. Please make sure your email settings are correct and that you are not being blocked by your ISP.')
