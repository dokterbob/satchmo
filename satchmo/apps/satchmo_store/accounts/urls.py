"""
URLConf for Django user registration.

Recommended usage is to use a call to ``include()`` in your project's
root URLConf to include this URLConf for any URL beginning with
'/accounts/'.

"""
from django.conf.urls.defaults import *
from livesettings import config_value

# extending the urls in contacts
from satchmo_store.contact.urls import urlpatterns
from signals_ahoy.signals import collect_urls
from satchmo_store import accounts


# Activation keys get matched by \w+ instead of the more specific
# [a-fA-F0-9]+ because a bad activation key should still get to the view;
# that way it can return a sensible "invalid key" message instead of a
# confusing 404.
urlpatterns += patterns('satchmo_store.accounts.views',
    (r'^activate/(?P<activation_key>\w+)/$', 'activate', {}, 'registration_activate'),
    (r'^login/$', 'emaillogin', {'template_name': 'registration/login.html'}, 'auth_login'),
    (r'^register/$', 'register', {}, 'registration_register'),
    (r'^secure/login/$', 'emaillogin', {'SSL' : True, 'template_name': 'registration/login.html'}, 'auth_secure_login'),    
)

urlpatterns += patterns('',
    ('^logout/$','django.contrib.auth.views.logout', {'template_name': 'registration/logout.html'}, 'auth_logout'),
    )

verify = (config_value('SHOP', 'ACCOUNT_VERIFICATION') == 'EMAIL')

urlpatterns += patterns('django.views.generic',
    (r'^register/complete/$', 'simple.direct_to_template',
        {'template': 'registration/registration_complete.html',
        'extra_context': {'verify': verify }}, 
        'registration_complete'),
)

#Dictionary for authentication views
password_reset_dict = {
    'template_name': 'registration/password_reset_form.html',
    'email_template_name': 'registration/password_reset.txt',
}

# the "from email" in password reset is problematic... it is hard coded as None
urlpatterns += patterns('django.contrib.auth.views',
    (r'^password_reset/$', 'password_reset', password_reset_dict, 'auth_password_reset'),
    (r'^password_reset/done/$', 'password_reset_done', {'template_name':'registration/password_reset_done.html'}, 'auth_password_reset_done'),
    (r'^password_change/$', 'password_change', {'template_name':'registration/password_change_form.html'}, 'auth_password_change'),
    (r'^password_change/done/$', 'password_change_done', {'template_name':'registration/password_change_done.html'}, 'auth_change_done'),
    (r'^reset/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/$', 'password_reset_confirm'),
    (r'^reset/done/$', 'password_reset_complete'),
)

collect_urls.send(sender=accounts, patterns=urlpatterns)
