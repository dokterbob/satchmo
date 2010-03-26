from django import forms
from django import http
from django.core import urlresolvers
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils.translation import ugettext_lazy as _
from satchmo_store.mail import send_store_mail
from satchmo_store.shop.signals import contact_sender
import logging

log = logging.getLogger('satchmo_store.shop.views')

# Choices displayed to the user to categorize the type of contact request.
email_choices = (
    ("General Question", _("General question")),
    ("Order Problem", _("Order problem")),
)

class ContactForm(forms.Form):
    name = forms.CharField(label=_("Name"), max_length=100)
    sender = forms.EmailField(label=_("Email address"), max_length=75)
    subject = forms.CharField(label=_("Subject"))
    inquiry = forms.ChoiceField(label=_("Inquiry"), choices=email_choices)
    contents = forms.CharField(label=_("Contents"), widget=
        forms.widgets.Textarea(attrs={'cols': 40, 'rows': 5}))

def form(request):
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            new_data = form.cleaned_data
            c = {
                'request_type': new_data['inquiry'],
                'name': new_data['name'],
                'email': new_data['sender'],
                'request_text': new_data['contents'] }
            subject = new_data['subject']
            send_store_mail(subject, c, 'shop/email/contact_us.txt',
                            send_to_store=True, sender=contact_sender)
            url = urlresolvers.reverse('satchmo_contact_thanks')
            return http.HttpResponseRedirect(url)
    else: #Not a post so create an empty form
        initialData = {}
        if request.user.is_authenticated():
            initialData['sender'] = request.user.email
            initialData['name'] = request.user.first_name + " " + request.user.last_name
        form = ContactForm(initial=initialData)

    return render_to_response('shop/contact_form.html', {'form': form},
                              context_instance=RequestContext(request))
