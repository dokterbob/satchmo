from satchmo_ext.upsell.models import Upsell, UpsellTranslation
from django.contrib import admin
from django.utils.translation import get_language, ugettext_lazy as _


class UpsellTranslation_Inline(admin.TabularInline):
    model = UpsellTranslation
    extra = 1

class UpsellOptions(admin.ModelAdmin):
    fieldsets = (
        (None, {'fields': ('target', 'goal', 'style', 'notes', 'create_date')}), )
    inlines = [UpsellTranslation_Inline]
    filter_horizontal = ('target',)

admin.site.register(Upsell, UpsellOptions)

