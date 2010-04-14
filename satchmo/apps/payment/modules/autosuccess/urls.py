from django.conf.urls.defaults import patterns
from satchmo_store.shop.satchmo_settings import get_satchmo_setting
ssl = get_satchmo_setting('SSL', default_value=False)

urlpatterns = patterns('',
     (r'^$', 'payment.modules.autosuccess.views.one_step', {'SSL': ssl}, 'AUTOSUCCESS_satchmo_checkout-step2'),
     (r'^success/$', 'payment.views.checkout.success', {'SSL': ssl}, 'AUTOSUCCESS_satchmo_checkout-success'),
)
