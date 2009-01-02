from shipping.modules.tiered.models import Carrier, ShippingTier, CarrierTranslation
from django.contrib import admin
from django.utils.translation import get_language, ugettext_lazy as _

class ShippingTier_Inline(admin.TabularInline):
    model = ShippingTier
    extra = 6
    ordering = ('min_total', 'expires')

class CarrierTranslation_Inline(admin.TabularInline):
    model = CarrierTranslation
    ordering = ('carrier',)
    extra = 1

class CarrierOptions(admin.ModelAdmin):
    ordering = ('key',)
    inlines = [CarrierTranslation_Inline, ShippingTier_Inline, ]

admin.site.register(Carrier, CarrierOptions)


