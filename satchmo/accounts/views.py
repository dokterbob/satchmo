import logging
from django import http
from django import newforms as forms
from django.conf import settings
from django.core import urlresolvers
from django.contrib.auth import logout, login, authenticate
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.shortcuts import render_to_response
from django.template import loader
from django.template import RequestContext, Context
from django.utils.translation import ugettext_lazy as _, ugettext
from satchmo.contact.models import Contact
from satchmo.shop.models import Config
from satchmo.shop.utils.unique_id import generate_id
from socket import error as SocketError
from satchmo.configuration import config_get_group, config_value, SettingNotSet

log = logging.getLogger('satchmo.accounts.views')

YESNO = (
    (1, _('Yes')),
    (0, _('No'))
)

class RegistrationForm(forms.Form):
    """The basic account registration form."""
    email = forms.EmailField(label=_('Email address'), max_length=30, required=True)
    password2 = forms.CharField(label=_('Password (again)'), max_length=30, widget=forms.PasswordInput(), required=True)
    password = forms.CharField(label=_('Password'), max_length=30, widget=forms.PasswordInput(), required=True)
    first_name = forms.CharField(label=_('First name'), max_length=30, required=True)
    last_name = forms.CharField(label=_('Last name'), max_length=30, required=True)
    newsletter = forms.BooleanField(label=_('Newsletter'), widget=forms.CheckboxInput(), required=False)

    def clean_password(self):
        """Enforce that password and password2 are the same."""
        p1 = self.cleaned_data.get('password')
        p2 = self.cleaned_data.get('password2')
        if not (p1 and p2 and p1 == p2):
            raise forms.ValidationError(ugettext("The two passwords do not match."))

        # note, here is where we'd put some kind of custom validator to enforce "hard" passwords.
        return p1

    def clean_email(self):
        """Prevent account hijacking by disallowing duplicate emails."""
        email = self.cleaned_data.get('email', None)
        if email and User.objects.filter(email=email).count() > 0:
            raise forms.ValidationError(ugettext("That email address is already in use."))

        return email

def send_welcome_email(email, first_name, last_name):
    t = loader.get_template('registration/welcome.txt')
    shop_config = Config.get_shop_config()
    shop_email = shop_config.store_email
    subject = ugettext("Welcome to %s") % shop_config.store_name
    c = Context({
        'first_name': first_name,
        'last_name': last_name,
        'company_name': shop_config.store_name,
        'site_url': shop_config.site.domain,
    })
    body = t.render(c)
    try:
        send_mail(subject, body, shop_email, [email], fail_silently=False)
    except SocketError, e:
        if settings.DEBUG:
            log.error('Error sending mail: %s' % e)
            log.warn('Ignoring email error, since you are running in DEBUG mode.  Email was:\nTo:%s\nSubject: %s\n---\n%s', email, subject, body)
        else:
            log.fatal('Error sending mail: %s' % e)
            raise IOError('Could not send email, please check to make sure your email settings are correct, and that you are not being blocked by your ISP.')

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

            data = form.cleaned_data
            password = data['password']
            email = data['email']
            first_name = data['first_name']
            last_name = data['last_name']
            username = generate_id(first_name, last_name)

            verify = (config_value('SHOP', 'ACCOUNT_VERIFICATION') == 'EMAIL')
            if verify:
                from registration.models import RegistrationProfile
                user = RegistrationProfile.objects.create_inactive_user(
                    username, password, email, send_email=True)
            else:
                user = User.objects.create_user(username, email, password)

            user.first_name = first_name
            user.last_name = last_name
            user.save()

            # If the user already has a contact, retrieve it.
            # Otherwise, create a new one.
            try:
                contact = Contact.objects.from_request(request, create=False)
                
            except Contact.DoesNotExist:
                contact = Contact()

            contact.user = user
            contact.first_name = first_name
            contact.last_name = last_name
            contact.email = email                
            contact.role = 'Customer'
            contact.save()
            
            if config_get_group('NEWSLETTER'):
                from satchmo.newsletter import update_subscription
                if 'newsletter' not in data:
                    subscribed = False
                else:
                    subscribed = data['newsletter']

                update_subscription(contact, subscribed)

            if not verify:
                user = authenticate(username=username, password=password)
                login(request, user)
                send_welcome_email(email, first_name, last_name)

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
            contact = None

        if contact and config_get_group('NEWSLETTER'):
            from satchmo.newsletter import is_subscribed
            current_subscriber = is_subscribed(contact)
        else:
            current_subscriber = False

        initial_data['newsletter'] = current_subscriber

        form = RegistrationForm(initial=initial_data)

    return (False, form)

def register(request, redirect=None, template='registration/registration_form.html'):
    """
    Allows a new user to register an account.
    """

    success, todo = register_handle_form(request, redirect=redirect)
    if success:
        return todo
    else:
        if config_get_group('NEWSLETTER'):
            show_newsletter = True
        else:
            show_newsletter = False
                
        context = RequestContext(request, {
            'form': todo, 
            'title' : _('Registration Form'),
            'show_newsletter' : show_newsletter
            })
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
        request.session['custID'] = contact.id
        send_welcome_email(contact.email, contact.first_name, contact.last_name)

    context = RequestContext(request, {
        'account': account,
        'expiration_days': config_value('SHOP', 'ACCOUNT_ACTIVATION_DAYS'),
    })
    return render_to_response('registration/activate.html', context)

def shop_logout(request):
    logout(request)
    if 'custID' in request.session:
        del request.session['custID']
    return http.HttpResponseRedirect('%s/' % (settings.SHOP_BASE))

