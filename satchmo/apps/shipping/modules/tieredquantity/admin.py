from shipping.modules.tieredquantity.models import Carrier, QuantityTier, CarrierTranslation
from django.contrib import admin
from django.utils.translation import get_language, ugettext_lazy as _

class QuantityTier_Inline(admin.TabularInline):
    model = QuantityTier
    extra = 5
    ordering = ('quantity', 'expires')

class CarrierTranslation_Inline(admin.TabularInline):
    model = CarrierTranslation
    extra = 1

class CarrierOptions(admin.ModelAdmin):
    ordering = ('key',)
    inlines = [CarrierTranslation_Inline, QuantityTier_Inline]

admin.site.register(Carrier, CarrierOptions)

