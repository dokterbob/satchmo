from django.conf.urls.defaults import *

urlpatterns = patterns('satchmo',
     (r'^$', 'payment.modules.autosuccess.views.one_step', {'SSL':False}, 'AUTOSUCCESS_satchmo_checkout-step2'),
     (r'^success/$', 'payment.common.views.checkout.success', {'SSL':False}, 'AUTOSUCCESS_satchmo_checkout-success'),
)
