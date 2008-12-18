from satchmo.contact.models import Organization, Contact, Interaction, PhoneNumber, AddressBook
from satchmo.utils.admin import AutocompleteAdmin
from django.contrib import admin
from django.utils.translation import get_language, ugettext_lazy as _

class Contact_Inline(admin.TabularInline):
    model = Contact
    extra = 1

class PhoneNumber_Inline(admin.TabularInline):
    model = PhoneNumber
    extra = 1

class AddressBook_Inline(admin.StackedInline):
    model = AddressBook
    extra = 1


class OrganizationOptions(admin.ModelAdmin):
    list_filter = ['type', 'role']
    list_display = ['name', 'type', 'role']

class ContactOptions(AutocompleteAdmin):
    list_display = ('last_name', 'first_name', 'organization', 'role')
    list_filter = ['create_date', 'role', 'organization']
    ordering = ['last_name']
    search_fields = ('first_name', 'last_name', 'email')
    related_search_fields = {'user': ('username', 'first_name', 'last_name', 'email')}
    related_string_functions = {'user': lambda u: u"%s (%s)" % (u.username, u.get_full_name())}
    inlines = [PhoneNumber_Inline, AddressBook_Inline]

class InteractionOptions(admin.ModelAdmin):
    list_filter = ['type', 'date_time']


admin.site.register(Organization, OrganizationOptions)
admin.site.register(Contact, ContactOptions)
admin.site.register(Interaction, InteractionOptions)
