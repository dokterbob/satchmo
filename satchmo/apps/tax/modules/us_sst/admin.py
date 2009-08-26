from django.contrib import admin
from django.forms import models, ValidationError
from django.utils.translation import get_language, ugettext_lazy as _
from models import TaxBoundry, TaxRate, Taxable

ADDRESS_FIELDS = (
    'oddEven', 'lowAddress', 'highAddress',
    'streetPreDirection', 'streetName', 'streetSuffix', 'streetPostDirection',
    'addressSecondaryAbbr', 'addressSecondaryOddEven',
    'addressSecondaryLow', 'addressSecondaryHigh',
    'cityName', 'zipCode', 'plus4',
)

ZIP_FIELDS = ('zipCodeLow','zipExtensionLow','zipCodeHigh','zipExtensionHigh')

RATE_FIELDS = (
    'serCode',
    'fipsStateCode',
    'fipsStateIndicator',
    'fipsCountyCode',
    'fipsPlaceCode',
    'fipsPlaceType',
    'special_1_code',
    'special_1_type',
    'special_2_code',
    'special_2_type',
    'special_3_code',
    'special_3_type',
    'special_4_code',
    'special_4_type',
    'special_5_code',
    'special_5_type',
    'special_6_code',
    'special_6_type',
    'special_7_code',
    'special_7_type',
    'special_8_code',
    'special_8_type',
    'special_9_code',
    'special_9_type',
    'special_10_code',
    'special_10_type',
    'special_11_code',
    'special_11_type',
    'special_12_code',
    'special_12_type',
    'special_13_code',
    'special_13_type',
    'special_14_code',
    'special_14_type',
    'special_15_code',
    'special_15_type',
    'special_16_code',
    'special_16_type',
    'special_17_code',
    'special_17_type',
    'special_18_code',
    'special_18_type',
    'special_19_code',
    'special_19_type',
    'special_20_code',
    'special_20_type', 
)

class TaxBoundryOptions(admin.ModelAdmin):
    fieldsets = (
        (None, {
            'fields': ('recordType', 'startDate', 'endDate')
        }),
        ('Zip and +4 Records',{
            'classes': ('collapse',),
            'fields': ZIP_FIELDS,
        }),
        ('Address Records', {
            'classes': ('collapse',),
            'fields': ADDRESS_FIELDS,
        }),
        ('Rates', {
            'fields': RATE_FIELDS,
        })
    )
    list_display = ('recordType', 'startDate', 'endDate', 'zip_range', 'streetName', 'cityName', 'zipCode',)

class TaxBoundryForm(models.ModelForm):

    def clean(self):
        type = self.cleaned_data['recordType']
        if type in ('4', 'Z'):
            for field in ADDRESS_FIELDS:
                self.cleaned_data[field] = None
        if type == 'Z':
            self.cleaned_data['zipExtensionLow'] = None
            self.cleaned_data['zipExtensionHigh'] = None
            low = self.cleaned_data['zipCodeLow']
            high = self.cleaned_data['zipCodeHigh']
            if high is None or low is None:
                raise ValidationError(_("Zip-5 records need a high and a low."))
        elif type == '4':
            low = self.cleaned_data['zipCodeLow']
            high = self.cleaned_data['zipCodeHigh']
            low_ext = self.cleaned_data['zipExtensionLow']
            high_ext = self.cleaned_data['zipExtensionHigh']
            if high is None or low is None or low_ext is None or high_ext is None:
                raise ValidationError(_("Zip+4 records need a high and a low for both parts."))
        else:
            for field in ZIP_FIELDS:
                self.cleaned_data[field] = None
            for field in ('lowAddress', 'highAddress', 'streetName', 'cityName',
                          'zipCode', 'plus4',):
                if not self.cleaned_data[field]:
                    raise ValidationError(_('Address rocord needs: low, high, street, city, zip, zip+4'))
        return super(TaxBoundryForm, self).clean()

class TaxRateOptions(admin.ModelAdmin):
    list_display = ('state',
                    'jurisdictionType', 'jurisdictionFipsCode',
                    'startDate', 'endDate',
                    'generalRateIntrastate', 'generalRateInterstate',
                    'foodRateIntrastate', 'foodRateInterstate'
    )

#class TaxRateOptions(admin.ModelAdmin):
#
#    jurisdictionType = models.CharField(max_length=2,
#        verbose_name=_('Jurisdiction Type'))
#    jurisdictionFipsCode = models.CharField(max_length=5,
#        verbose_name=_('Jurisdiction FIPS Code'))
#    generalRateIntrastate = models.DecimalField(max_digits=8, decimal_places=7,
#        verbose_name=_('General Tax Rate - Intrastate'))
#    generalRateInterstate = models.DecimalField(max_digits=8, decimal_places=7,
#        verbose_name=_('General Tax Rate - Interstate'))
#    foodRateIntrastate = models.DecimalField(max_digits=8, decimal_places=7,
#        verbose_name=_('Food/Drug Tax Rate - Intrastate'))
#    foodRateInterstate = models.DecimalField(max_digits=8, decimal_places=7,
#        verbose_name=_('Food/Drug Tax Rate - Interstate'))
#    startDate = models.DateField(verbose_name=_('Effective Start Date'))
#    endDate = models.DateField(verbose_name=_('Effective End Date'))
##
#    def clean(self):
#        tax_zone = self.cleaned_data['taxZone']
#        tax_country = self.cleaned_data['taxCountry']
#        if tax_zone and not tax_country or not tax_zone and tax_country:
#            return super(TaxRateForm, self).clean()
#        else:
#            raise ValidationError(_("You must choose a zone or a country."))
#
#class TaxRateOptions(admin.ModelAdmin):
#    list_display = ("taxClass", "taxZone", "taxCountry", "display_percentage")
#    form = TaxRateForm
#

admin.site.register(TaxBoundry, TaxBoundryOptions)
admin.site.register(TaxRate, TaxRateOptions)
admin.site.register(Taxable)
#admin.site.register(TaxCollected)
