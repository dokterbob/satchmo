from satchmo.shipping.modules.tiered.models import Carrier, ShippingTier
from django.contrib import admin
from django.utils.translation import get_language, ugettext_lazy as _


class CarrierOptions(admin.ModelAdmin):
    ordering = ('key',)

class ShippingTierOptions(admin.ModelAdmin):
    ordering = ('min_total', 'expires')

admin.site.register(Carrier, CarrierOptions)
admin.site.register(ShippingTier, ShippingTierOptions)

