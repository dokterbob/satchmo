from satchmo.newsletter.models import Subscription
from django.contrib import admin
from django.utils.translation import get_language, ugettext_lazy as _


class SubscriptionOptions(admin.ModelAdmin):
    list_display = ['email', 'subscribed', 'create_date', 'update_date']
    list_filter = ['subscribed']

admin.site.register(Subscription, SubscriptionOptions)

