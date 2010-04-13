from django.conf.urls.defaults import patterns
from satchmo_store.shop.satchmo_settings import get_satchmo_setting

ssl = get_satchmo_setting('SSL', default_value=False)

urlpatterns = patterns('',
     (r'^$', 'payment.modules.paypal.views.pay_ship_info', {'SSL': ssl}, 'PAYPAL_satchmo_checkout-step2'),
     (r'^confirm/$', 'payment.modules.paypal.views.confirm_info', {'SSL': ssl}, 'PAYPAL_satchmo_checkout-step3'),
     (r'^success/$', 'payment.views.checkout.success', {'SSL': ssl}, 'PAYPAL_satchmo_checkout-success'),
     (r'^ipn/$', 'payment.modules.paypal.views.ipn', {'SSL': ssl}, 'PAYPAL_satchmo_checkout-ipn'),
     (r'^confirmorder/$', 'payment.views.confirm.confirm_free_order',
         {'SSL' : ssl, 'key' : 'PAYPAL'}, 'PAYPAL_satchmo_checkout_free-confirm')
)
