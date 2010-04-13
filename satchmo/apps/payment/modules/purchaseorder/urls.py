from django.conf.urls.defaults import patterns
from satchmo_store.shop.satchmo_settings import get_satchmo_setting

ssl = get_satchmo_setting('SSL', default_value=False)

urlpatterns = patterns('payment',
    (r'^$', 'modules.purchaseorder.views.pay_ship_info',
       {'SSL':ssl}, 'PURCHASEORDER_satchmo_checkout-step2'),

    (r'^confirm/$', 'modules.purchaseorder.views.confirm_info',
       {'SSL':ssl}, 'PURCHASEORDER_satchmo_checkout-step3'),

     (r'^success/$', 'views.checkout.success',
        {'SSL':ssl}, 'PURCHASEORDER_satchmo_checkout-success'),
)
