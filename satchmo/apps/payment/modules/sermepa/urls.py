#
#   SERMEPA / ServiRed payments module for Satchmo
#
#   Author: Michal Salaban <michal (at) salaban.info>
#   with a great help of Fluendo S.A., Barcelona
#
#   Based on "Guia de comercios TPV Virtual SIS" ver. 5.18, 15/11/2008, SERMEPA
#   For more information about integration look at http://www.sermepa.es/
#
#   TODO: SERMEPA interface provides possibility of recurring payments, which
#   could be probably used for SubscriptionProducts. This module doesn't support it.
#
from django.conf.urls.defaults import *
from livesettings import config_get_group

config = config_get_group('PAYMENT_SERMEPA')

urlpatterns = patterns('',
    (r'^$', 'payment.modules.sermepa.views.pay_ship_info', {'SSL': config.SSL.value}, 'SERMEPA_satchmo_checkout-step2'),
    (r'^confirm/$', 'payment.modules.sermepa.views.confirm_info', {'SSL': config.SSL.value}, 'SERMEPA_satchmo_checkout-step3'),
    (r'^success/$', 'payment.views.checkout.success', {'SSL': config.SSL.value}, 'SERMEPA_satchmo_checkout-success'),
    (r'^failure/$', 'payment.views.checkout.failure', {'SSL': config.SSL.value}, 'SERMEPA_satchmo_checkout-failure'),
    (
        r'^notify/$',
        'payment.modules.sermepa.views.notify_callback',
        {'SSL': config.SSL.value},
        'SERMEPA_satchmo_checkout-notify_callback'
        ),
    (r'^confirmorder/$', 'payment.views.confirm.confirm_free_order', 
       {'SSL' : config.SSL.value, 'key' : 'SERMEPA'}, 'SERMEPA_satchmo_checkout_free-confirm')
)
