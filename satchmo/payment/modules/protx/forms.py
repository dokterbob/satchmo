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
    
    def save(self, orderpayment):
        cc = super(ProtxPayShipForm, self).save(orderpayment)
        
        data = self.cleaned_data
        
        cc.card_holder=data.get('card_holder', '')
        cc.start_month=data.get('month_start', None)
        cc.start_year=data.get('year_start', None)
        cc.issue_num=data.get('issue_num', '')
        cc.save()
        
        return cc