from django.conf.urls.defaults import *

urlpatterns = patterns('',
     (r'^$', 'payment.modules.autosuccess.views.one_step', {'SSL':False}, 'AUTOSUCCESS_satchmo_checkout-step2'),
     (r'^success/$', 'payment.views.checkout.success', {'SSL':False}, 'AUTOSUCCESS_satchmo_checkout-success'),
)
