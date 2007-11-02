from django.conf.urls.defaults import *
from satchmo.configuration import config_get_group

config = config_get_group('PAYMENT_PAYPAL')

urlpatterns = patterns('satchmo',
     (r'^$', 'payment.modules.paypal.views.pay_ship_info', {'SSL': config.SSL.value}, 'PAYPAL_satchmo_checkout-step2'),
     (r'^confirm/$', 'payment.modules.paypal.views.confirm_info', {'SSL': config.SSL.value}, 'PAYPAL_satchmo_checkout-step3'),
     (r'^success/$', 'payment.common.views.checkout.success', {'SSL': config.SSL.value}, 'PAYPAL_satchmo_checkout-success'),
)
