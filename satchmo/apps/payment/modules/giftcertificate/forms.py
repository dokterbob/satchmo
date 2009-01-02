from django import forms
from django.utils.translation import ugettext_lazy as _
from payment.forms import SimplePayShipForm

class GiftCertCodeForm(forms.Form):
    code = forms.CharField(_('Code'), required=True)
    
class GiftCertPayShipForm(SimplePayShipForm):
    giftcode = forms.CharField(max_length=100)

    def __init__(self, request, paymentmodule, *args, **kwargs):
        super(GiftCertPayShipForm, self).__init__(request, paymentmodule, *args, **kwargs)
