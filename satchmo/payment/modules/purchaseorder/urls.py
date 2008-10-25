from django.conf.urls.defaults import *
from satchmo.configuration import config_get_group

config = config_get_group('PAYMENT_PURCHASEORDER')

urlpatterns = patterns('satchmo.payment',
    (r'^$', 'modules.purchaseorder.views.pay_ship_info', 
       {'SSL':config.SSL.value}, 'PURCHASEORDER_satchmo_checkout-step2'),

    (r'^confirm/$', 'modules.purchaseorder.views.confirm_info', 
       {'SSL':config.SSL.value}, 'PURCHASEORDER_satchmo_checkout-step3'),

     (r'^success/$', 'views.checkout.success', 
        {'SSL':config.SSL.value}, 'PURCHASEORDER_satchmo_checkout-success'),
)
