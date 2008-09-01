from satchmo.discount.models import Discount
from django.contrib import admin
from django.utils.translation import get_language, ugettext_lazy as _


class DiscountOptions(admin.ModelAdmin):
    list_display=('site', 'description','active')
    list_display_links = ('description',)
    filter_horizontal = ('validProducts',)

admin.site.register(Discount, DiscountOptions)

