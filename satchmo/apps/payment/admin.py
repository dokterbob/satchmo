from payment.models import CreditCardDetail
from django.contrib import admin


class CreditCardDetail_Inline(admin.StackedInline):
    model = CreditCardDetail
    extra = 1


