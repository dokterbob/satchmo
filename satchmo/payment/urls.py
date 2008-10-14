from django.conf.urls.defaults import *
from satchmo.configuration import config_get_group, config_get, config_value
import logging

log = logging.getLogger('payment.urls')

config = config_get_group('PAYMENT')

urlpatterns = patterns('satchmo.payment.views',
     (r'^$', 'contact.contact_info_view', {'SSL': config.SSL.value}, 'satchmo_checkout-step1'),
     (r'custom/charge/(?P<orderitem_id>\d+)/$', 'balance.charge_remaining', {}, 'satchmo_charge_remaining'),
     (r'custom/charge/$', 'balance.charge_remaining_post', {}, 'satchmo_charge_remaining_post'),
     (r'^balance/(?P<order_id>\d+)/$', 'balance.balance_remaining_order', {'SSL' : config.SSL.value}, 'satchmo_balance_remaining_order'),
     (r'^balance/$', 'balance.balance_remaining', {'SSL' : config.SSL.value}, 'satchmo_balance_remaining'),
     (r'^cron/$', 'cron.cron_rebill', {}, 'satchmo_cron_rebill'),
     (r'^mustlogin/$', 'contact.authentication_required', {'SSL' : config.SSL.value}, 'satchmo_checkout_auth_required'),
)

# now add all enabled module payment settings

def make_urlpatterns():
    patterns = []
    for key in config_value('PAYMENT', 'MODULES'):
        cfg = config_get(key, 'MODULE')
        modulename = cfg.editor_value
        urlmodule = "%s.urls" % modulename
        patterns.append(url(config_value(key, 'URL_BASE'), [urlmodule]))
    return tuple(patterns)
    
urlpatterns += make_urlpatterns()

