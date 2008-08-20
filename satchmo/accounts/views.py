import logging
import signals
from django import http
from django.conf import settings
from django.contrib.auth import logout, login
from django.core import urlresolvers
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils.translation import ugettext_lazy as _
from forms import RegistrationForm
from mail import send_welcome_email
from satchmo.configuration import config_get_group, config_value
from satchmo.contact import CUSTOMER_ID
from satchmo.contact.models import Contact
from satchmo.shop import get_satchmo_setting

log = logging.getLogger('satchmo.accounts.views')

YESNO = (
    (1, _('Yes')),
    (0, _('No'))
)

def register_handle_form(request, redirect=None):
    """
    Handle all registration logic.  This is broken out from "register" to allow easy overriding/hooks
    such as a combined login/register page.

    Returns:
    - Success flag
    - HTTPResponseRedirect (success) or form (fail)
    """

    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            contact = form.save(request)

            if not redirect:
                redirect = urlresolvers.reverse('registration_complete')
            return (True, http.HttpResponseRedirect(redirect))

    else:
        initial_data = {}
        try:
            contact = Contact.objects.from_request(request, create=False)
            initial_data = {
                'email': contact.email,
                'first_name': contact.first_name,
                'last_name': contact.last_name }
        except Contact.DoesNotExist:
            log.debug("No contact in request")
            contact = None

        signals.satchmo_registration_initialdata.send(contact,
            contact=contact,
            initial_data=initial_data)
                
        form = RegistrationForm(initial=initial_data)

    return (False, form)

def register(request, redirect=None, template='registration/registration_form.html'):
    """
    Allows a new user to register an account.
    """

    ret = register_handle_form(request, redirect)
    success = ret[0]
    todo = ret[1]
    if len(ret) > 2:
        extra_context = ret[2]
    else:
        extra_context = {}
        
    if success:
        return todo
    else:
        if config_get_group('NEWSLETTER'):
            show_newsletter = True
        else:
            show_newsletter = False
                
        ctx = {
            'form': todo, 
            'title' : _('Registration Form'),
            'show_newsletter' : show_newsletter
        }
        
        if extra_context:
            ctx.update(extra_context)
            
        context = RequestContext(request, ctx)
        return render_to_response(template, context)

def activate(request, activation_key):
    """
    Activates a user's account, if their key is valid and hasn't
    expired.
    """
    from registration.models import RegistrationProfile
    activation_key = activation_key.lower()
    account = RegistrationProfile.objects.activate_user(activation_key)

    if account:
        # ** hack for logging in the user **
        # when the login form is posted, user = authenticate(username=data['username'], password=data['password'])
        # ...but we cannot authenticate without password... so we work-around authentication
        account.backend = settings.AUTHENTICATION_BACKENDS[0]
        login(request, account)
        contact = Contact.objects.get(user=account)
        request.session[CUSTOMER_ID] = contact.id
        send_welcome_email(contact.email, contact.first_name, contact.last_name)
        signals.satchmo_registration_verified.send(contact, contact=contact)

    context = RequestContext(request, {
        'account': account,
        'expiration_days': config_value('SHOP', 'ACCOUNT_ACTIVATION_DAYS'),
    })
    return render_to_response('registration/activate.html', context)

def shop_logout(request):
    logout(request)
    if CUSTOMER_ID in request.session:
        del request.session[CUSTOMER_ID]
    return http.HttpResponseRedirect('%s/' % (get_satchmo_setting('SHOP_BASE')))

