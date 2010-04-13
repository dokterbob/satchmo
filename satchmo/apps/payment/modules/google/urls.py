from django.conf.urls.defaults import patterns
from satchmo_store.shop.satchmo_settings import get_satchmo_setting

ssl = get_satchmo_setting('SSL', default_value=False)

urlpatterns = patterns('',
     (r'^$', 'payment.modules.google.views.pay_ship_info', {'SSL': ssl}, 'GOOGLE_satchmo_checkout-step2'),
     (r'^confirm/$', 'payment.modules.google.views.confirm_info', {'SSL': ssl}, 'GOOGLE_satchmo_checkout-step3'),
     (r'^success/$', 'payment.modules.google.views.success', {'SSL': ssl}, 'GOOGLE_satchmo_checkout-success'),
     (r'^notification/$', 'payment.modules.google.views.notification', {'SSL': ssl},
        'GOOGLE_satchmo_checkout-notification'),
     (r'^confirmorder/$', 'payment.views.confirm.confirm_free_order',
        {'SSL' : ssl, 'key' : 'GOOGLE'}, 'GOOGLE_satchmo_checkout_free-confirm')
)
