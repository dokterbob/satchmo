from django import forms
from django.utils.translation import ugettext_lazy as _
from payment.forms import SimplePayShipForm
from django.contrib.sites.models import Site
from models import GiftCertificate
from decimal import Decimal

class GiftCertCodeForm(forms.Form):
    code = forms.CharField(_('Code'), required=True)
       
class GiftCertPayShipForm(SimplePayShipForm):
    giftcode = forms.CharField(max_length=100)

    def __init__(self, request, paymentmodule, *args, **kwargs):
        super(GiftCertPayShipForm, self).__init__(request, paymentmodule, *args, **kwargs)
    
    def clean_giftcode(self):
        gc_code = self.cleaned_data['giftcode']
        if gc_code:
            try:
                gc = GiftCertificate.objects.get(code=gc_code, valid=True, 
                    site=Site.objects.get_current())
            except GiftCertificate.DoesNotExist:
                raise forms.ValidationError(_('Invalid gift certificate code.'))
            if gc.balance == Decimal('0'):
                raise forms.ValidationError(_('Gift certificate balance is 0.'))
        return gc_code
