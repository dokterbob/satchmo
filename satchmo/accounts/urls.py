"""
URLConf for Django user registration.

Recommended usage is to use a call to ``include()`` in your project's
root URLConf to include this URLConf for any URL beginning with
'/accounts/'.

"""
from django.conf.urls.defaults import *
from satchmo.configuration import config_value

# extending the urls in contacts
from satchmo.contact.urls import urlpatterns

# Activation keys get matched by \w+ instead of the more specific
# [a-fA-F0-9]+ because a bad activation key should still get to the view;
# that way it can return a sensible "invalid key" message instead of a
# confusing 404.
urlpatterns += patterns('satchmo.accounts.views',
    (r'^activate/(?P<activation_key>\w+)/$', 'activate', {}, 'registration_activate'),
    (r'^logout/$', 'shop_logout', {}, 'auth_logout'),
    (r'^register/$', 'register', {}, 'registration_register'),
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
    (r'^login/$', 'login', {'template_name': 'registration/login.html'}, 'auth_login'),
    (r'^password_reset/$', 'password_reset', password_reset_dict, 'auth_password_reset'),
    (r'^password_reset/done/$', 'password_reset_done', {'template_name':'registration/password_reset_done.html'}, 'auth_password_reset_done'),
    (r'^password_change/$', 'password_change', {'template_name':'registration/password_change_form.html'}, 'auth_password_change'),
    (r'^password_change/done/$', 'password_change_done', {'template_name':'registration/password_change_done.html'}, 'auth_change_done'),
)
