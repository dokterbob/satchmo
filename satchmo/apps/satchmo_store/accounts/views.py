from django.conf import settings
from django.contrib.auth import login, REDIRECT_FIELD_NAME
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.sites.models import Site, RequestSite
from django.core import urlresolvers
from django.http import HttpResponseRedirect, QueryDict
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.cache import never_cache
from forms import RegistrationAddressForm, RegistrationForm, EmailAuthenticationForm
from l10n.models import Country
from livesettings import config_get_group, config_value
from satchmo_store.accounts.mail import send_welcome_email
from satchmo_store.accounts import signals
from satchmo_store.contact import CUSTOMER_ID
from satchmo_store.contact.models import Contact
from satchmo_store.shop.models import Config, Cart

import logging

log = logging.getLogger('satchmo_store.accounts.views')

YESNO = (
    (1, _('Yes')),
    (0, _('No'))
)

def emaillogin(request, template_name='registration/login.html', 
    auth_form=EmailAuthenticationForm, redirect_field_name=REDIRECT_FIELD_NAME):
    "Displays the login form and handles the login action. Altered to use the EmailAuthenticationForm"

    redirect_to = request.REQUEST.get(redirect_field_name, '')

    # Avoid redirecting to logout if the user clicked on login after logout
    if redirect_to == urlresolvers.reverse('auth_logout'):
        redirect_to = None

    success, todo = _login(request, redirect_to)
    if success:
        # return the response redirect
        return todo
    else:
        # continue with the login form
        form = todo

    request.session.set_test_cookie()
    if Site._meta.installed:
        current_site = Site.objects.get_current()
    else:
        current_site = RequestSite(request)

    return render_to_response(template_name, {
        'form': form,
        redirect_field_name: redirect_to,
        'site_name': current_site.name,
    }, context_instance=RequestContext(request))
emaillogin = never_cache(emaillogin)

def _login(request, redirect_to, auth_form=EmailAuthenticationForm):
    """"Altered version of the default login, intended to be called by `combined_login`.

    Returns tuple:
    - success
    - redirect (success) or form (on failure)
    """
    
    if request.method == 'POST':
        form = auth_form(data=request.POST)
        if form.is_valid():
            # Light security check -- make sure redirect_to isn't garbage.
            if not redirect_to or '//' in redirect_to or ' ' in redirect_to:
                redirect_to = settings.LOGIN_REDIRECT_URL
            login(request, form.get_user())
            if request.session.test_cookie_worked():
                request.session.delete_test_cookie()
                if config_value('SHOP','PERSISTENT_CART'):
                    _get_prev_cart(request)
            return (True, HttpResponseRedirect(redirect_to))
        else:
            log.debug(form.errors)
    else:
        form = auth_form(request)

    return (False, form)

def _get_prev_cart(request):
    try:
        contact = request.user.contact_set.get()
        saved_cart = contact.cart_set.latest('date_time_created')
        # If the latest cart has len == 0, cart is unusable.
        if len(saved_cart) and request.session['cart']:
            # Merge the two carts together
            existing_cart = Cart.objects.from_request(request, create=False)
            saved_cart.merge_carts(existing_cart)
            request.session['cart'] = saved_cart.id
    except Exception, e:
        pass


def register_handle_address_form(request, redirect=None):
    """
    Handle all registration logic.  This is broken out from "register" to allow easy overriding/hooks
    such as a combined login/register page.
    
    This handler allows a login or a full registration including address.

    Returns:
    - Success flag
    - HTTPResponseRedirect (success) or form (fail)
    - A dictionary with extra context fields
    """

    shop = Config.objects.get_current()
    try:
        contact = Contact.objects.from_request(request)
    except Contact.DoesNotExist:
        contact = None

    if request.method == 'POST':

        form = RegistrationAddressForm(request.POST, shop=shop, contact=contact)

        if form.is_valid():
            contact = form.save(request)

            if not redirect:
                redirect = urlresolvers.reverse('registration_complete')
            return (True, HttpResponseRedirect(redirect))

    else:
        initial_data = {}
        if contact:
            initial_data = {
                'email': contact.email,
                'first_name': contact.first_name,
                'last_name': contact.last_name }
            address = contact.billing_address
            if address:
                initial_data['street1'] = address.street1
                initial_data['street2'] = address.street2
                initial_data['state'] = address.state
                initial_data['city'] = address.city
                initial_data['postal_code'] = address.postal_code
                try:
                    initial_data['country'] = address.country
                except Country.DoesNotExist:
                    USA = Country.objects.get(iso2_code__exact="US")    
                    initial_data['country'] = USA

        form = RegistrationAddressForm(initial=initial_data, shop=shop, contact=contact)

    return (False, form, {'country' : shop.in_country_only})


def register_handle_form(request, redirect=None):
    """
    Handle all registration logic.  This is broken out from "register" to allow easy overriding/hooks
    such as a combined login/register page.
    
    This method only presents a typical login or register form, not a full address form 
    (see register_handle_address_form for that one.)

    Returns:
    - Success flag
    - HTTPResponseRedirect (success) or form (fail)
    """

    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            contact = form.save(request)

            # look for explicit "next"
            next = request.POST.get('next', '')
            if not next:
                if redirect:
                    next = redirect
                else:
                    next = urlresolvers.reverse('registration_complete')
            return (True, HttpResponseRedirect(next))

    else:
        initial_data = {}
        try:
            contact = Contact.objects.from_request(request, create=False)
            initial_data = {
                'email': contact.email,
                'first_name': contact.first_name,
                'last_name': contact.last_name,
            }
        except Contact.DoesNotExist:
            log.debug("No contact in request")
            contact = None
            
        initial_data['next'] = request.GET.get('next', '') 

        form = RegistrationForm(initial=initial_data)

    return (False, form)



#---- Views

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
        _login(request, account)
        contact = Contact.objects.get(user=account)
        request.session[CUSTOMER_ID] = contact.id
        send_welcome_email(contact.email, contact.first_name, contact.last_name)
        signals.satchmo_registration_verified.send(contact, contact=contact)

    context = RequestContext(request, {
        'account': account,
        'expiration_days': config_value('SHOP', 'ACCOUNT_ACTIVATION_DAYS'),
    })
    return render_to_response('registration/activate.html',
                              context_instance=context)


def login_signup(request, template_name="contact/login_signup.html", registration_handler=register_handle_form):
    """Display/handle a combined login and create account form"""

    redirect_to = request.REQUEST.get(REDIRECT_FIELD_NAME, '')

    loginform = None
    createform = None
    extra_context = {}

    if request.POST:
        action = request.POST.get('action', 'login')
        if action == 'create':
            #log.debug('Signup form')
            ret = registration_handler(request, redirect=redirect_to)
            success = ret[0]
            todo = ret[1]
            if len(ret) > 2:
                extra_context = ret[2]

            if success:
                #log.debug('Successful %s form submit, sending to reg complete page')
                if redirect_to:
                    return HttpResponseRedirect(redirect_to)
                else:
                    ctx = RequestContext(request, {
                        REDIRECT_FIELD_NAME: redirect_to,
                    })

                    return render_to_response('registration/registration_complete.html',
                                              context_instance=ctx)
            else:
                createform = todo

        else:
            #log.debug('Login form')
            success, todo = _login(request, redirect_to)
            if success:
                return todo
            else:
                loginform = todo

        request.POST = QueryDict("")
        

    else:
        request.session.set_test_cookie()

    if not loginform:
        success, loginform = _login(request, redirect_to)
    if not createform:
        ret = registration_handler(request, redirect_to)
        success = ret[0]
        createform = ret[1]
        if len(ret) > 2:
            extra_context = ret[2]

    site = Site.objects.get_current()

    if config_get_group('NEWSLETTER'):
        show_newsletter = True
    else:
        show_newsletter = False


    ctx = {
        'loginform': loginform,
        'createform' : createform,
        REDIRECT_FIELD_NAME: redirect_to,
        'site_name': site.name,
        'show_newsletter' : show_newsletter,
    }

    if extra_context:
        ctx.update(extra_context)            

    context = RequestContext(request, ctx)

    return render_to_response(template_name, context_instance=context)


def login_signup_address(request, template_name="contact/login_signup_address.html"):
    """
    View which allows a user to login or else fill out a full address form.
    """
    return login_signup(request, template_name=template_name, registration_handler=register_handle_address_form)


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
        return render_to_response(template, context_instance=context)

