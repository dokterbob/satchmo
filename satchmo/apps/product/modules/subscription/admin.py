from django.contrib import admin
from product.modules.subscription.models import SubscriptionProduct, Trial

class Trial_Inline(admin.StackedInline):
    model = Trial
    extra = 2


class SubscriptionProductOptions(admin.ModelAdmin):
    inlines = [Trial_Inline]

admin.site.register(SubscriptionProduct, SubscriptionProductOptions)

