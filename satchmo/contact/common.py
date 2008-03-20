from satchmo.l10n.models import Country
from satchmo.shop.models import Config
from django.utils.translation import ugettext, ugettext_lazy as _

selection = _("Please Select")

def get_area_country_options(request):
    """Return form data for area and country selection in address forms
    """
    shop_config = Config.get_shop_config()
    local_only = shop_config.in_country_only
    default_iso2 = shop_config.sales_country
    if (default_iso2):
        default_iso2 = default_iso2.iso2_code
    else:
        default_iso2 = 'US'

    if local_only:
        iso2 = default_iso2
    else:
        iso2 = request.GET.get('iso2', default_iso2)

    default_country = Country.objects.get(iso2_code=iso2)

    options = {}
    areas = countries = None

    area_choices = default_country.adminarea_set.filter(active=True)
    if area_choices:
        areas = [('', selection)]
        for area in area_choices:
            value_to_choose = (area.abbrev or area.name, ugettext(area.name))
            areas.append(value_to_choose)

    if not local_only:
        options['country'] = default_country.iso2_code
        countries = [(default_country.iso2_code, ugettext(default_country.printable_name))]
        for country in shop_config.shipping_countries.filter(active=True):
            country_to_choose = (country.iso2_code, ugettext(country.printable_name))
            #Make sure the default only shows up once
            if country.iso2_code != default_country.iso2_code:
                countries.append(country_to_choose)

    return (areas, countries, local_only and default_country or None)
