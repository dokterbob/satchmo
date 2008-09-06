from django.core.exceptions import ImproperlyConfigured
from django.utils.translation import ugettext, ugettext_lazy as _
from satchmo.l10n.models import Country
from satchmo.shop.models import Config

selection = _("Please Select")

def get_area_country_options(request):
    """Return form data for area and country selection in address forms
    """
    shop_config = Config.objects.get_current()
    local_only = shop_config.in_country_only
    default_country = shop_config.sales_country
    if not default_country:
        raise ImproperlyConfigured("In country only is set, but there is no sales country defined in the Shop Config for this site.")

    countries = None
    areas = default_country.adminarea_set.filter(active=True)

    if not local_only:
        countries = shop_config.shipping_countries.filter(active=True)
        
    return (areas, countries, local_only and default_country or None)
