from satchmo_ext.newsletter.models import Subscription, SubscriptionAttribute
from django.contrib import admin
from django.utils.translation import get_language, ugettext_lazy as _
    
class SubscriptionAttributeInline(admin.TabularInline):
    model = SubscriptionAttribute
    extra = 1

class SubscriptionOptions(admin.ModelAdmin):
    list_display = ['email', 'subscribed', 'create_date', 'update_date']
    list_filter = ['subscribed']
    inlines = [SubscriptionAttributeInline,]

admin.site.register(Subscription, SubscriptionOptions)

