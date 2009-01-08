from django.conf.urls.defaults import *
from livesettings import config_get_group

config = config_get_group('PAYMENT_GIFTCERTIFICATE')

urlpatterns = patterns('',
     (r'^$', 'payment.modules.giftcertificate.views.pay_ship_info', {'SSL':config.SSL.value}, 'GIFTCERTIFICATE_satchmo_checkout-step2'),
     (r'^confirm/$', 'payment.modules.giftcertificate.views.confirm_info', {'SSL':config.SSL.value}, 'GIFTCERTIFICATE_satchmo_checkout-step3'),
     (r'^success/$', 'payment.views.checkout.success', {'SSL':config.SSL.value}, 'GIFTCERTIFICATE_satchmo_checkout-success'),
     (r'^balance/$', 'payment.modules.giftcertificate.views.check_balance', {}, 'satchmo_giftcertificate_balance'),
)
