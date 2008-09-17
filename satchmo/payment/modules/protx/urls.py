import os
from django.conf.urls.defaults import *
from satchmo.payment.paymentsettings import PaymentSettings

SSL = PaymentSettings().PROTX.SSL

urlpatterns = patterns('satchmo',
     (r'^$', 'payment.modules.protx.views.pay_ship_info', {'SSL':SSL}, 'PROTX_satchmo_checkout-step2'),
     (r'^confirm/$', 'payment.modules.protx.views.confirm_info', {'SSL':SSL}, 'PROTX_satchmo_checkout-step3'),
     (r'^success/$', 'shop.views.common.checkout_success', {'SSL':SSL}, 'PROTX_satchmo_checkout-success'),
     (r'^secure3d/$', 'payment.modules.protx.views.confirm_secure3d', {'SSL':SSL}, 'PROTX_satchmo_checkout-secure3d'),
)