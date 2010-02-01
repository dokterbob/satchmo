from django.conf.urls.defaults import *
from django.db import models
from livesettings import config_get_group, config_get, config_value
from livesettings.models import SettingNotSet
import logging

log = logging.getLogger('payment.urls')

config = config_get_group('PAYMENT')

urlpatterns = patterns('payment.views',
     (r'^$', 'contact.contact_info_view', {'SSL': config.SSL.value}, 'satchmo_checkout-step1'),
     (r'^success/$', 'checkout.success', {'SSL' : config.SSL.value}, 'satchmo_checkout-success'),
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
    for app in models.get_apps():
        if hasattr(app, 'PAYMENT_PROCESSOR'):
            parts = app.__name__.split('.')
            key = parts[-2].upper()
            modulename = 'PAYMENT_%s' % key
            name = app.__name__
            name = name[:name.rfind('.')]
            #log.debug('payment module=%s, key=%s', modulename, key)
            # BJK: commenting out Bursar settings here
            # try:
            #     cfg = config_get(modulename, 'INTERFACE_MODULE')
            #     interface = cfg.editor_value
            # except SettingNotSet:
            #     interface = name[:name.rfind('.')]
            # urlmodule = "%s.urls" % interface
            urlmodule = '.'.join(parts[:-1]) + '.urls'
            urlbase = config_value(modulename, 'URL_BASE')
            log.debug('Found payment processor: %s, adding urls at %s', key, urlbase)
            patterns.append(url(urlbase, [urlmodule, '', '']))
    return tuple(patterns)
    
urlpatterns += make_urlpatterns()
