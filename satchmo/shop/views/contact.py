from django import forms
from django import http
from django.conf import settings
from django.core.mail import send_mail
from django.shortcuts import render_to_response
from django.template import loader
from django.template import RequestContext, Context
from django.utils.translation import ugettext_lazy as _
from satchmo.shop import get_satchmo_setting
from satchmo.shop.models import Config
from socket import error as SocketError
import logging
from django.core import urlresolvers

log = logging.getLogger('satchmo.shop.views')

# Choices displayed to the user to categorize the type of contact request.
email_choices = (
    ("General Question", _("General question")),
    ("Order Problem", _("Order problem")),
)

class ContactForm(forms.Form):
    name = forms.CharField(label=_("Name"), max_length=100)
    sender = forms.EmailField(label=_("Email address"))
    subject = forms.CharField(label=_("Subject"))
    inquiry = forms.ChoiceField(label=_("Inquiry"), choices=email_choices)
    contents = forms.CharField(label=_("Contents"), widget=
        forms.widgets.Textarea(attrs={'cols': 40, 'rows': 5}))

def form(request):
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            new_data = form.cleaned_data
            t = loader.get_template('email/contact_us.txt')
            c = Context({
                'request_type': new_data['inquiry'],
                'name': new_data['name'],
                'email': new_data['sender'],
                'request_text': new_data['contents'] })
            subject = new_data['subject']
            shop_config = Config.objects.get_current()
            shop_email = shop_config.store_email
            if not shop_email:
                log.warn('No email address configured for the shop.  Using admin settings.')
                shop_email = settings.ADMINS[0][1]
            try:
                body = t.render(c)
                send_mail(subject, body, shop_email,
                         [shop_email], fail_silently=False)
            except SocketError, e:
                if settings.DEBUG:
                    log.error('Error sending mail: %s' % e)
                    log.warn('Ignoring email error, since you are running in DEBUG mode.  Email was:\nTo:%s\nSubject: %s\n---\n%s', shop_email, subject, body)
                else:
                    log.fatal('Error sending mail: %s' % e)
                    raise IOError('Could not send email. Please make sure your email settings are correct and that you are not being blocked by your ISP.')
            url = urlresolvers.reverse('satchmo_contact_thanks')
            return http.HttpResponseRedirect(url)
    else: #Not a post so create an empty form
        initialData = {}
        if request.user.is_authenticated():
            initialData['sender'] = request.user.email
            initialData['name'] = request.user.first_name + " " + request.user.last_name
        form = ContactForm(initial=initialData)

    return render_to_response('contact_form.html', {'form': form},
        RequestContext(request))

