from django.conf.urls.defaults import *
from livesettings import config_value, config_get_group

config = config_get_group('PAYMENT_AUTOSUCCESS')

urlpatterns = patterns('',
     (r'^$', 'payment.modules.autosuccess.views.one_step', {'SSL':False}, 'AUTOSUCCESS_satchmo_checkout-step2'),
     (r'^success/$', 'payment.views.checkout.success', {'SSL':False}, 'AUTOSUCCESS_satchmo_checkout-success'),
)
