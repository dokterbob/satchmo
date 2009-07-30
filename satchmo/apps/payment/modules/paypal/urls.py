from django.conf.urls.defaults import *
from livesettings import config_get_group

config = config_get_group('PAYMENT_PAYPAL')

urlpatterns = patterns('',
     (r'^$', 'payment.modules.paypal.views.pay_ship_info', {'SSL': config.SSL.value}, 'PAYPAL_satchmo_checkout-step2'),
     (r'^confirm/$', 'payment.modules.paypal.views.confirm_info', {'SSL': config.SSL.value}, 'PAYPAL_satchmo_checkout-step3'),
     (r'^success/$', 'payment.views.checkout.success', {'SSL': config.SSL.value}, 'PAYPAL_satchmo_checkout-success'),
     (r'^ipn/$', 'payment.modules.paypal.views.ipn', {'SSL': config.SSL.value}, 'PAYPAL_satchmo_checkout-ipn'),
     (r'^confirmorder/$', 'payment.views.confirm.confirm_free_order', 
        {'SSL' : config.SSL.value, 'key' : 'PAYPAL'}, 'PAYPAL_satchmo_checkout_free-confirm')
)
