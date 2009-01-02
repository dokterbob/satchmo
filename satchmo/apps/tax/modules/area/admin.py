from django.contrib import admin
from django.forms import models, ValidationError
from django.utils.translation import get_language, ugettext_lazy as _
from models import TaxRate

class TaxRateForm(models.ModelForm):

    def clean(self):
        tax_zone = self.cleaned_data['taxZone']
        tax_country = self.cleaned_data['taxCountry']
        if tax_zone and not tax_country or not tax_zone and tax_country:
            return super(TaxRateForm, self).clean()
        else:
            raise ValidationError(_("You must choose a zone or a country."))
        
class TaxRateOptions(admin.ModelAdmin):
    list_display = ("taxClass", "taxZone", "taxCountry", "display_percentage")
    form = TaxRateForm
    
admin.site.register(TaxRate, TaxRateOptions)

