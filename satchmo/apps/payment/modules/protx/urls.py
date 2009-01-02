from django.conf.urls.defaults import *
from livesettings import config_get_group

config = config_get_group('PAYMENT_PROTX')

urlpatterns = patterns('',
     (r'^$', 'payment.modules.protx.views.pay_ship_info', 
        {'SSL':config.SSL.value}, 'PROTX_satchmo_checkout-step2'),

     (r'^confirm/$', 'payment.modules.protx.views.confirm_info', 
        {'SSL':config.SSL.value}, 'PROTX_satchmo_checkout-step3'),

    (r'^secure3d/$', 'payment.modules.protx.views.confirm_secure3d', 
       {'SSL':config.SSL.value}, 'PROTX_satchmo_checkout-secure3d'),

     (r'^success/$', 'payment.views.checkout.success', 
        {'SSL':config.SSL.value}, 'PROTX_satchmo_checkout-success'),
)