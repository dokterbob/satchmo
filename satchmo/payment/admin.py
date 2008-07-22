from satchmo.payment.models import PaymentOption, CreditCardDetail
from django.contrib import admin
from django.utils.translation import get_language, ugettext_lazy as _


class CreditCardDetail_Inline(admin.StackedInline):
    model = CreditCardDetail
    extra = 1

class PaymentOptionOptions(admin.ModelAdmin):
    list_display = ['optionName','description','active']
    ordering = ['sortOrder']

admin.site.register(PaymentOption, PaymentOptionOptions)

