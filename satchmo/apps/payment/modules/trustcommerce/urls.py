from django.conf.urls.defaults import *
from livesettings import config_value, config_get_group


config = config_get_group('PAYMENT_TRUSTCOMMERCE')

urlpatterns = patterns('',
     (r'^$', 'payment.modules.trustcommerce.views.pay_ship_info', {'SSL':config.SSL.value}, 'TRUSTCOMMERCE_satchmo_checkout-step2'),
     (r'^confirm/$', 'payment.modules.trustcommerce.views.confirm_info', {'SSL':config.SSL.value}, 'TRUSTCOMMERCE_satchmo_checkout-step3'),
     (r'^success/$', 'payment.views.checkout.success', {'SSL':config.SSL.value}, 'TRUSTCOMMERCE_satchmo_checkout-success'),
)