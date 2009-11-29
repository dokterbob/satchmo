from l10n.models import Country, AdminArea
from django.contrib import admin
from django.utils.translation import get_language, ugettext_lazy as _


class AdminArea_Inline(admin.TabularInline):
    model = AdminArea
    extra = 1

class CountryOptions(admin.ModelAdmin):
    
    def make_active(self, request, queryset):
        rows_updated = queryset.update(active=True)
        if rows_updated == 1:
            message_bit = _("1 country was")
        else:
            message_bit = _("%s countries were" % rows_updated)
        self.message_user(request, _("%s successfully marked as active") % message_bit)
    make_active.short_description = _("Mark selected countries as active")
    
    def make_inactive(self, request, queryset):
        rows_updated = queryset.update(active=False)
        if rows_updated == 1:
            message_bit = _("1 country was")
        else:
            message_bit = _("%s countries were" % rows_updated)
        self.message_user(request, _("%s successfully marked as inactive") % message_bit)
    make_inactive.short_description = _("Mark selected countries as inactive")
    
    list_display = ('printable_name', 'iso2_code','active')
    list_filter = ('continent', 'active')
    search_fields = ('name', 'iso2_code', 'iso3_code')
    actions = ('make_active', 'make_inactive')
    inlines = [AdminArea_Inline]

admin.site.register(Country, CountryOptions)

