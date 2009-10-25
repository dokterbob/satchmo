# coding=UTF-8
from django.db import models
from django.utils.translation import ugettext, ugettext_lazy as _
from product.models import TaxClass
from l10n.models import AdminArea, Country
#from satchmo_store.shop.models import Order
#from satchmo_store.shop.signals import order_success
#from tax import Processor

from datetime import date as _date

try:
    from decimal import Decimal
except:
    from django.utils._decimal import Decimal

class Taxable(models.Model):
    """
    Map that says what items are taxable in a jurisdiction.

    To use properly, assign products to a meaningful TaxClass, such as 'Shipping',
    'Food', 'Default'. Then create rules for the jurisdictions where you are
    required to collect tax. If for example, you are taxing objects in two states
    and 'Food' is taxable in one and not the other, but shipping is the other
    way around, you would need to create the following entries:

    food = TaxClass(...)
    default = TaxClass(...)
    shipping = TaxClass(...)

    one_state = AdminArea(...)
    two_state = AdminArea(...)
    usa = Country(...)

    Taxable(taxClass=default,  isTaxable=True,  taxZone=one_state, taxCountry=usa)
    Taxable(taxClass=food,     isTaxable=False, useFood=True, taxZone=one_state, taxCountry=usa)
    Taxable(taxClass=shipping, isTaxable=True,  taxZone=one_state, taxCountry=usa)
    Taxable(taxClass=default,  isTaxable=True,  taxZone=two_state, taxCountry=usa)
    Taxable(taxClass=food,     isTaxable=True,  useFood=True, taxZone=two_state, taxCountry=usa)
    Taxable(taxClass=shipping, isTaxable=False, taxZone=two_state, taxCountry=usa)

    Laws vary drastically form state to state, so please make sure to make needed
    TaxClasses for all objects that vary in taxing jurisdictions to which you
    must submit.

    If you do not at least create a 'Default' entry for a state, then you will
    not be collecting any taxes for that state. Only create entires for states
    where you are obligated to collect and report taxes.

    SST defines food rates and interstate vs. intrastate rates. You may override
    these, otherwise taxes will be charged at the non-food, intrastate rate by default.

    WARNING: If a product is taxable in ANY jurisdiction, it must be set taxable
    in the product. You disable it per-jurisdiction by disabling it here. You
    cannot enable it here if it is disabled on the product itself.
    """
    taxClass = models.ForeignKey(TaxClass, verbose_name=_('Tax Class'))
    taxZone = models.ForeignKey(AdminArea, blank=True, null=True,
        verbose_name=_('Tax Zone'))
    taxCountry = models.ForeignKey(Country, blank=True, null=True,
        verbose_name=_('Tax Country'))
    isTaxable = models.BooleanField(verbose_name=_('Taxable?'), default=True, )
    useIntrastate = models.BooleanField(verbose_name=_('Use Intrastate rate instead of Interstate?'),
                                        default=True)
    useFood = models.BooleanField(verbose_name=_('Use food/drug rate instead of general?'),
                                  default=False)

    def _country(self):
        if self.taxZone:
            return self.taxZone.country.name
        else:
            return self.taxCountry.name
    country = property(_country)

    #def _display_percentage(self):
    #    return "%#2.2f%%" % (100*self.percentage)
    #_display_percentage.short_description = _('Percentage')
    #display_percentage = property(_display_percentage)

    def __unicode__(self):
        return u"%s - %s = %s" % (self.taxClass,
                             self.taxZone and self.taxZone or self.taxCountry,
                             self.isTaxable)

    class Meta:
        verbose_name = _("Taxable Class")
        verbose_name_plural = _("Taxable Classes")

JURISDICTION_CHOICES = (
    (0, 'County'),
    (1, 'City'),
    (2, 'Town'),
    (3, 'Village'),
    (4, 'Borough'),
    (5, 'Township'),
    (9, 'Other Municipality'),
    (10, 'School District'),
    (11, 'Junior Colleges'),
    (19, 'Other Schools'),
    (20, 'Water Control'),
    (21, 'Utility District'),
    (22, 'Sanitation'),
    (23, 'Water or Sewer District'),
    (24, 'Reclamation District'),
    (25, 'Fire or Police'),
    (26, 'Roads or Bridges'),
    (27, 'Hospitals'),
    (29, 'Other Municipal Services'),
    (40, 'Township and County'),
    (41, 'City and School'),
    (42, 'County collected by Other Taxing Authority'),
    (43, 'State and County'),
    (44, 'Central Collection Taxing Authority'),
    (45, 'State Taxing Authority'),
    (49, 'Other Combination Collection'),
    (50, 'Bond Authority'),
    (51, 'Annual County Bond Authority'),
    (52, 'Semi-annual County Bond Authority'),
    (53, 'Annual City Bond Authority'),
    (54, 'Semi-annual City Bond Authority'),
    (59, 'Other Bond Authority'),
    (61, 'Assessment District'),
    (62, 'Homeowner’s Association'),
    (63, 'Special District'),
    (69, 'Other Special Districts'),
    (70, 'Central Appraisal Taxing Authority'),
    (71, 'Unsecured County Taxes'),
    (72, 'Mobile Home Authority'),
    (79, 'Other Special Applications'),
)

class TaxRate(models.Model):
    """
    Records for tax rates in the default SST format as defined at:
    http://www.streamlinedsalestax.org/Technology/RatesandBoundariesClean082605.pdf
    """
    state = models.IntegerField(max_length=2,
        verbose_name=_('FIPS State Code'), db_index=True)
    jurisdictionType = models.IntegerField(max_length=2, choices=JURISDICTION_CHOICES,
        verbose_name=_('Type'))
    jurisdictionFipsCode = models.CharField(max_length=5,
        verbose_name=_('FIPS Code'), db_index=True)
    generalRateIntrastate = models.DecimalField(max_digits=8, decimal_places=7,
        verbose_name=_('General Tax Rate - Intrastate'))
    generalRateInterstate = models.DecimalField(max_digits=8, decimal_places=7,
        verbose_name=_('General Tax Rate - Interstate'))
    foodRateIntrastate = models.DecimalField(max_digits=8, decimal_places=7,
        verbose_name=_('Food/Drug Tax Rate - Intrastate'))
    foodRateInterstate = models.DecimalField(max_digits=8, decimal_places=7,
        verbose_name=_('Food/Drug Tax Rate - Interstate'))
    startDate = models.DateField(verbose_name=_('Effective Start Date'))
    endDate = models.DateField(verbose_name=_('Effective End Date'))

    class Meta:
        verbose_name = _("Tax Rate")
        verbose_name_plural = _("Tax Rates")

    def __unicode__(self):
        return u'State %d: Jurisdiction: %s(%s)' % (
            self.state,
            self.jurisdictionFipsCode,
            self.get_jurisdictionType_display(),
        )

    def rate(self, intrastate=False, food=False):
        if intrastate:
            if food:
                return self.foodRateIntrastate
            else:
                return self.generalRateIntrastate
        else:
            if food:
                return self.foodRateInterstate
            else:
                return self.generalRateInterstate

TAX_BOUNDRY_CHOICES = (
    ('Z', 'Zip-5 Record'),
    ('4', 'Zip+4 Record'),
    ('A', 'Address Record'),
)
ODD_EVEN_CHOICES = (
    ('O', 'Odd'),
    ('E', 'Even'),
    ('B', 'Both'),

)
class TaxBoundry(models.Model):
    """
    Records for tax boundries in the default SST format as defined at:
    http://www.streamlinedsalestax.org/Technology/RatesandBoundariesClean082605.pdf
    """
    recordType = models.CharField(max_length=1, choices=TAX_BOUNDRY_CHOICES,
        verbose_name=_('Boundry Type'))
    startDate = models.DateField(verbose_name=_('Effective Start Date'))
    endDate = models.DateField(verbose_name=_('Effective End Date'))
    lowAddress = models.IntegerField(blank=True, null=True,
        verbose_name=_('Low Address Range'))
    highAddress = models.IntegerField(blank=True, null=True,
        verbose_name=_('High Address Range'))
    oddEven = models.CharField(max_length=1, blank=True, null=True, choices=ODD_EVEN_CHOICES,
        verbose_name=_('Odd / Even Range Indicator'))
    streetPreDirection = models.CharField(max_length=2, blank=True, null=True,
        verbose_name=_('State Pre-Directional Abbr.'))
    streetName = models.CharField(max_length=20, blank=True, null=True,
        verbose_name=_('Street Name'))
    streetSuffix = models.CharField(max_length=4, blank=True, null=True,
        verbose_name=_('Street Suffix Abbr.'))
    streetPostDirection = models.CharField(max_length=2, blank=True, null=True,
        verbose_name=_('Street Post Directional'))
    addressSecondaryAbbr = models.CharField(max_length=4, blank=True, null=True,
        verbose_name=_('Address Secondary - Abbr.'))
    addressSecondaryLow = models.IntegerField(blank=True, null=True,
        verbose_name=_('Address Secondary - Low'))
    addressSecondaryHigh = models.IntegerField(max_length=8, blank=True, null=True,
        verbose_name=_('Address Secondary - High'))
    addressSecondaryOddEven = models.CharField(max_length=1, blank=True, null=True,
        choices=ODD_EVEN_CHOICES, verbose_name=_('Address Secondary - Odd/Even'))
    cityName = models.CharField(max_length=28, blank=True, null=True,
        verbose_name=_('City Name'))
    zipCode = models.IntegerField(blank=True, null=True,
        verbose_name=_('Zip Code'))
    plus4 = models.IntegerField(blank=True, null=True,
        verbose_name=_('Zip Code - Plus 4'))
    zipCodeLow = models.IntegerField(blank=True, null=True,
        verbose_name=_('Zip Code - Low'), db_index=True)
    zipExtensionLow = models.IntegerField(blank=True, null=True,
        verbose_name=_('Zip Code Extension - Low'), db_index=True)
    zipCodeHigh = models.IntegerField(blank=True, null=True,
        verbose_name=_('Zip Code - High'), db_index=True)
    zipExtensionHigh = models.IntegerField(blank=True, null=True,
        verbose_name=_('Zip Code Extension - High'), db_index=True)
    serCode = models.CharField(max_length=5, verbose_name=_('Composite SER Code'), blank=True, null=True)
    fipsStateCode = models.CharField(max_length=2, blank=True, null=True,
        verbose_name=_('FIPS State Code'))
    fipsStateIndicator = models.CharField(max_length=2, blank=True, null=True,
        verbose_name=_('FIPS State Indicator'))
    fipsCountyCode = models.CharField(max_length=3, blank=True, null=True,
        verbose_name=_('FIPS County Code'))
    fipsPlaceCode = models.CharField(max_length=5, blank=True, null=True,
        verbose_name=_('FIPS Place Code'))
    fipsPlaceType = models.CharField(max_length=2, blank=True, null=True,
        verbose_name=_('FIPS Place Type'), choices=JURISDICTION_CHOICES)
    special_1_code = models.CharField(max_length=5, verbose_name=_('FIPS Special 1 code'), blank=True, null=True)
    special_1_type = models.CharField(max_length=2, verbose_name=_('FIPS Special 1 type'), blank=True, null=True, choices=JURISDICTION_CHOICES)
    special_2_code = models.CharField(max_length=5, verbose_name=_('FIPS Special 2 code'), blank=True, null=True)
    special_2_type = models.CharField(max_length=2, verbose_name=_('FIPS Special 2 type'), blank=True, null=True, choices=JURISDICTION_CHOICES)
    special_3_code = models.CharField(max_length=5, verbose_name=_('FIPS Special 3 code'), blank=True, null=True)
    special_3_type = models.CharField(max_length=2, verbose_name=_('FIPS Special 3 type'), blank=True, null=True, choices=JURISDICTION_CHOICES)
    special_4_code = models.CharField(max_length=5, verbose_name=_('FIPS Special 4 code'), blank=True, null=True)
    special_4_type = models.CharField(max_length=2, verbose_name=_('FIPS Special 4 type'), blank=True, null=True, choices=JURISDICTION_CHOICES)
    special_5_code = models.CharField(max_length=5, verbose_name=_('FIPS Special 5 code'), blank=True, null=True)
    special_5_type = models.CharField(max_length=2, verbose_name=_('FIPS Special 5 type'), blank=True, null=True, choices=JURISDICTION_CHOICES)
    special_6_code = models.CharField(max_length=5, verbose_name=_('FIPS Special 6 code'), blank=True, null=True)
    special_6_type = models.CharField(max_length=2, verbose_name=_('FIPS Special 6 type'), blank=True, null=True, choices=JURISDICTION_CHOICES)
    special_7_code = models.CharField(max_length=5, verbose_name=_('FIPS Special 7 code'), blank=True, null=True)
    special_7_type = models.CharField(max_length=2, verbose_name=_('FIPS Special 7 type'), blank=True, null=True, choices=JURISDICTION_CHOICES)
    special_8_code = models.CharField(max_length=5, verbose_name=_('FIPS Special 8 code'), blank=True, null=True)
    special_8_type = models.CharField(max_length=2, verbose_name=_('FIPS Special 8 type'), blank=True, null=True, choices=JURISDICTION_CHOICES)
    special_9_code = models.CharField(max_length=5, verbose_name=_('FIPS Special 9 code'), blank=True, null=True)
    special_9_type = models.CharField(max_length=2, verbose_name=_('FIPS Special 9 type'), blank=True, null=True, choices=JURISDICTION_CHOICES)
    special_10_code = models.CharField(max_length=5, verbose_name=_('FIPS Special 10 code'), blank=True, null=True)
    special_10_type = models.CharField(max_length=2, verbose_name=_('FIPS Special 10 type'), blank=True, null=True, choices=JURISDICTION_CHOICES)
    special_11_code = models.CharField(max_length=5, verbose_name=_('FIPS Special 11 code'), blank=True, null=True)
    special_11_type = models.CharField(max_length=2, verbose_name=_('FIPS Special 11 type'), blank=True, null=True, choices=JURISDICTION_CHOICES)
    special_12_code = models.CharField(max_length=5, verbose_name=_('FIPS Special 12 code'), blank=True, null=True)
    special_12_type = models.CharField(max_length=2, verbose_name=_('FIPS Special 12 type'), blank=True, null=True, choices=JURISDICTION_CHOICES)
    special_13_code = models.CharField(max_length=5, verbose_name=_('FIPS Special 13 code'), blank=True, null=True)
    special_13_type = models.CharField(max_length=2, verbose_name=_('FIPS Special 13 type'), blank=True, null=True, choices=JURISDICTION_CHOICES)
    special_14_code = models.CharField(max_length=5, verbose_name=_('FIPS Special 14 code'), blank=True, null=True)
    special_14_type = models.CharField(max_length=2, verbose_name=_('FIPS Special 14 type'), blank=True, null=True, choices=JURISDICTION_CHOICES)
    special_15_code = models.CharField(max_length=5, verbose_name=_('FIPS Special 15 code'), blank=True, null=True)
    special_15_type = models.CharField(max_length=2, verbose_name=_('FIPS Special 15 type'), blank=True, null=True, choices=JURISDICTION_CHOICES)
    special_16_code = models.CharField(max_length=5, verbose_name=_('FIPS Special 16 code'), blank=True, null=True)
    special_16_type = models.CharField(max_length=2, verbose_name=_('FIPS Special 16 type'), blank=True, null=True, choices=JURISDICTION_CHOICES)
    special_17_code = models.CharField(max_length=5, verbose_name=_('FIPS Special 17 code'), blank=True, null=True)
    special_17_type = models.CharField(max_length=2, verbose_name=_('FIPS Special 17 type'), blank=True, null=True, choices=JURISDICTION_CHOICES)
    special_18_code = models.CharField(max_length=5, verbose_name=_('FIPS Special 18 code'), blank=True, null=True)
    special_18_type = models.CharField(max_length=2, verbose_name=_('FIPS Special 18 type'), blank=True, null=True, choices=JURISDICTION_CHOICES)
    special_19_code = models.CharField(max_length=5, verbose_name=_('FIPS Special 19 code'), blank=True, null=True)
    special_19_type = models.CharField(max_length=2, verbose_name=_('FIPS Special 19 type'), blank=True, null=True, choices=JURISDICTION_CHOICES)
    special_20_code = models.CharField(max_length=5, verbose_name=_('FIPS Special 20 code'), blank=True, null=True)
    special_20_type = models.CharField(max_length=2, verbose_name=_('FIPS Special 20 type'), blank=True, null=True, choices=JURISDICTION_CHOICES)

    # Fill in this property to use not-today for looking up the tax rates.
    date = None
    # Set these and we'll use non-default rate.
    useIntrastate = None
    useFood = None

    def get_zip_range(self):
        if self.zipExtensionLow:
            return u'%05d-%04d -> %05d-%04d' % (
                self.zipCodeLow, self.zipExtensionLow, self.zipCodeHigh, self.zipExtensionHigh
            )
        else:
            return u'%05d -> %05d' % (self.zipCodeLow, self.zipCodeHigh)
    zip_range = property(get_zip_range)

    def rates(self, date=None):
        l = list()
        state = self.fipsStateCode
        
        if not date:
            date = _date.today()
            
        # Lookup all the applicable codes.
        for fips in (
            self.fipsStateIndicator, self.fipsCountyCode, self.fipsPlaceCode,
            self.special_1_code, self.special_2_code, self.special_3_code,
            self.special_4_code, self.special_5_code, self.special_6_code,
            self.special_7_code, self.special_8_code, self.special_9_code,
            self.special_10_code, self.special_11_code, self.special_12_code,
            self.special_13_code, self.special_14_code, self.special_15_code,
            self.special_16_code, self.special_17_code, self.special_18_code,
            self.special_19_code, self.special_20_code
        ):
            if not fips:
                continue
            
            rate = TaxRate.objects.get(
                state=state,
                jurisdictionFipsCode=fips,
                startDate__lte=date,
                endDate__gte=date,
            )
            l.append( rate  )
        
        return l

    def get_percentage(self, date=None):
        """
        Emulate being a tax rate by returning a total percentage to tax the customer.
        """
        pct = Decimal('0.00')
        for x in self.rates(date):
            pct += x.rate(intrastate=self.useIntrastate, food=self.useFood)
        return pct
    percentage=property(get_percentage)
    
    def __unicode__(self):
        if self.recordType == 'Z':
            return u'TaxBoundry(Z): %i -- %i' % (
                self.zipCodeLow, self.zipCodeHigh
            )
        elif self.recordType == '4':
            return u'TaxBoundry(4): %i-%i -- %i-%i' % (
                self.zipCodeLow, self.zipExtensionLow,
                self.zipCodeHigh, self.zipExtensionHigh,
            )
        else:
            return u'TaxBoundry(A)'

    @classmethod
    def lookup(cls, zip, ext=None, date=None):
        """Handy function to take a zip code and return the appropriate rates
        for it."""
        if not date:
            date = _date.today()
        
        # Try for a ZIP+4 lookup first if we can.
        if ext:
            try:
                return cls.objects.get(
                    recordType='4',
                    zipCodeLow__lte=zip,
                    zipCodeHigh__gte=zip,
                    zipExtensionLow__lte=ext,
                    zipExtensionHigh__gte=ext,
                    startDate__lte=date,
                    endDate__gte=date,
                )
            except cls.DoesNotExist:
                # Not all zip+4 have entires. That's OK.
                pass
        
        # Try for just the ZIP then.
        try:
            return cls.objects.get(
                recordType='Z',
                zipCodeLow__lte=zip,
                zipCodeHigh__gte=zip,
                startDate__lte=date,
                endDate__gte=date,
            )
        except cls.DoesNotExist:
            return None

    class Meta:
        verbose_name = _("Tax Boundry")
        verbose_name_plural = _("Tax Boundries")


#class TaxCollected(models.Model):
#    order = models.ForeignKey(Order, verbose_name=_("Order"))
#    taxRate = models.ForeignKey(TaxRate, verbose_name=_('Tax Rate'))
#    useIntrastate = models.BooleanField(verbose_name=_('Use Intrastate rate instead of Interstate?'),
#                                        default=True)
#    useFood = models.BooleanField(verbose_name=_('Use food/drug rate instead of general?'),
#                                  default=False)
#
#def save_taxes_collected(order, **kwargs):
#    processor = Processor(order=order)
#    tb = processor.get_boundry()
#

#order_success.connect(save_taxes_colletecd)

import config
