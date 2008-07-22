from satchmo.tax.models import TaxClass, TaxRate
from django.contrib import admin
from django.utils.translation import get_language, ugettext_lazy as _


class TaxRateOptions(admin.ModelAdmin):
    list_display = ("taxClass", "taxZone", "taxCountry", "display_percentage")

admin.site.register(TaxClass)
admin.site.register(TaxRate, TaxRateOptions)

