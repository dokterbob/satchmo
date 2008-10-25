from django import forms
from satchmo.payment import signals
from satchmo.payment.forms import SimplePayShipForm
from satchmo.payment.modules.purchaseorder.models import PurchaseOrder
from satchmo.utils import app_enabled
from django.core.exceptions import ImproperlyConfigured

class PurchaseorderPayShipForm(SimplePayShipForm):
    po_number = forms.CharField(max_length=20, required=False)
    
    def __init__(self, *args, **kwargs):
        if not app_enabled('purchaseorder'):
            raise ImproperlyConfigured('To use Purchase Order payment methods, you must have satchmo.payment.modules.purchaseorder in your INSTALLED_APPS')

        super(PurchaseorderPayShipForm, self).__init__(*args, **kwargs)
    
    def save(self, request, cart, contact, payment_module):
        """Save the order and the po information for this orderpayment"""
        super(PurchaseorderPayShipForm, self).save(request, cart, contact, payment_module)
        data = self.cleaned_data
        po = PurchaseOrder(po_number=data.get('po_number', ''), order=self.order)
        po.save()
        self.purchaseorder = po
        signals.form_save.send(PurchaseorderPayShipForm, form=self)
        
