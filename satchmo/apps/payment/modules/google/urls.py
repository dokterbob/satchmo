from django.conf.urls.defaults import *
from livesettings import config_get_group

config = config_get_group('PAYMENT_GOOGLE')

urlpatterns = patterns('',
     (r'^$', 'payment.modules.google.views.pay_ship_info', {'SSL': config.SSL.value}, 'GOOGLE_satchmo_checkout-step2'),
     (r'^confirm/$', 'payment.modules.google.views.confirm_info', {'SSL': config.SSL.value}, 'GOOGLE_satchmo_checkout-step3'),
     (r'^success/$', 'payment.modules.google.views.success', {'SSL': config.SSL.value}, 'GOOGLE_satchmo_checkout-success'),
     (r'^notification/$', 'payment.modules.google.views.notification', {'SSL': config.SSL.value},
        'GOOGLE_satchmo_checkout-notification'),
     (r'^confirmorder/$', 'payment.views.confirm.confirm_free_order', 
        {'SSL' : config.SSL.value, 'key' : 'GOOGLE'}, 'GOOGLE_satchmo_checkout_free-confirm')
)
