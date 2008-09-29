"""Protx Form"""
from django import forms
from satchmo.payment.common.forms import CreditPayShipForm, MONTHS

class ProtxPayShipForm(CreditPayShipForm):
    """Adds fields required by Prot/X to the Credit form."""
    
    card_holder = forms.CharField(max_length=30)
    month_start = forms.ChoiceField(choices=[(1, '--')]+MONTHS, required=False)
    year_start = forms.ChoiceField(required=False)
    issue_num = forms.CharField(max_length=2, required=False)
    
    def __init__(self, request, paymentmodule, *args, **kwargs):
        super(ProtxPayShipForm, self).__init__(request, paymentmodule, *args, **kwargs)
        cf = self.fields['card_holder']
        if cf.initial == "":
            user = request.user
            if user.contact_set.count() > 0:
                contact = user.contact_set.all()[0]
                cf.initial = contact.full_name

    def save(self, request, cart, contact, payment_module):
        """Save the order and the credit card details."""
        super(ProtxPayShipForm, self).save(request, cart, contact, payment_module)
                        
        self.cc.card_holder=data.get('card_holder', '')
        self.cc.start_month=data.get('month_start', None)
        self.cc.start_year=data.get('year_start', None)
        self.cc.issue_num=data.get('issue_num', '')
        self.cc.save()
