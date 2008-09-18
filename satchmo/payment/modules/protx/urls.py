import os
from django.conf.urls.defaults import *
from satchmo.payment.paymentsettings import PaymentSettings

config = config_get_group('PAYMENT_AUTHORIZENET')

urlpatterns = patterns('satchmo',
     (r'^$', 'payment.modules.protx.views.pay_ship_info', 
        {'SSL':config.SSL.value}, 'PROTX_satchmo_checkout-step2'),

     (r'^confirm/$', 'payment.modules.protx.views.confirm_info', 
        {'SSL':config.SSL.value}, 'PROTX_satchmo_checkout-step3'),

    (r'^secure3d/$', 'payment.modules.protx.views.confirm_secure3d', 
       {'SSL':config.SSL.value}, 'PROTX_satchmo_checkout-secure3d'),

     (r'^success/$', 'shop.views.common.checkout_success', 
        {'SSL':config.SSL.value}, 'PROTX_satchmo_checkout-success'),
)