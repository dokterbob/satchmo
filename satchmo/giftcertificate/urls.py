from django.conf.urls.defaults import *
from satchmo.configuration import config_get_group

config = config_get_group('PAYMENT_GIFTCERTIFICATE')

urlpatterns = patterns('satchmo',
     (r'^$', 'giftcertificate.views.pay_ship_info', {'SSL':config.SSL.value}, 'GIFTCERTIFICATE_satchmo_checkout-step2'),
     (r'^confirm/$', 'giftcertificate.views.confirm_info', {'SSL':config.SSL.value}, 'GIFTCERTIFICATE_satchmo_checkout-step3'),
     (r'^success/$', 'payment.common.views.checkout.success', {'SSL':config.SSL.value}, 'GIFTCERTIFICATE_satchmo_checkout-success'),
     (r'^balance/$', 'giftcertificate.views.check_balance', {}, 'satchmo_giftcertificate_balance'),
)
