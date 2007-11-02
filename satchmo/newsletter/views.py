from django import newforms as forms
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils.translation import ugettext_lazy as _, ugettext
from satchmo.newsletter import update_subscription as update_subscription_object
from satchmo.newsletter.models import get_contact_or_fake

class OptionalBoolean(forms.BooleanField):
    def __init__(self, *args, **kwargs):
        forms.BooleanField.__init__(self, *args, **kwargs)
        self.required = False

class NewsletterForm(forms.Form):
    full_name = forms.CharField(label=_('Full Name'), max_length=100, required=False)
    email = forms.EmailField(label=_('Email address'), max_length=50, required=True)
    subscribed = OptionalBoolean(label=_('Subscribe'), required=False, initial=True)

    def get_contact(self):
        data = self.cleaned_data
        email = data['email']
        full_name = data['full_name']
        
        return get_contact_or_fake(full_name, email)

def add_subscription(request, template="newsletter/subscribe_form.html", result_template="newsletter/update_results.html"):
    """Add a subscription and return the results in the requested template."""

    return _update(request, True, template, result_template)

def remove_subscription(request, template="newsletter/unsubscribe_form.html", result_template="newsletter/update_results.html"):
    """Remove a subscription and return the results in the requested template."""

    return _update(request, False, template, result_template)

def update_subscription(request, template="newsletter/update_form.html", result_template="newsletter/update_results.html"):
    """Add a subscription and return the results in the requested template."""

    return _update(request, 'FORM', template, result_template)

def _update(request, state, template, result_template):
    """Add a subscription and return the results in the requested template."""
    success = False

    if request.POST:
        form = NewsletterForm(request.POST)
        if form.is_valid():
            contact = form.get_contact()
            if state == 'FORM':
                state = form.cleaned_data['subscribed']
            result = update_subscription_object(contact, state)
            success = True
        else:
            result = ugettext('Error, not valid.')

    else:
        form = NewsletterForm()
        result = ""

    ctx = RequestContext(request, {
        'result' : result,
        'form' : form
    })

    if success:
        return render_to_response(result_template, ctx)
    else:
        return render_to_response(template, ctx)

