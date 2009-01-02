from django.conf.urls.defaults import *
from livesettings import config_value, config_get_group

config = config_get_group('PAYMENT_COD')

urlpatterns = patterns('',
     (r'^$', 'payment.modules.cod.views.pay_ship_info', {'SSL':config.SSL.value}, 'COD_satchmo_checkout-step2'),
     (r'^confirm/$', 'payment.modules.cod.views.confirm_info', {'SSL':config.SSL.value}, 'COD_satchmo_checkout-step3'),
     (r'^success/$', 'payment.views.checkout.success', {'SSL':config.SSL.value}, 'COD_satchmo_checkout-success'),
)
