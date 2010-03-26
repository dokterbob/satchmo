"""Protx Form"""
from django import forms
from django.utils.translation import ugettext as _
from payment.forms import CreditPayShipForm, MONTHS
from payment.modules.protx.config import REQUIRES_ISSUE_NUMBER
import logging

log = logging.getLogger('payment.protx.forms')

class ProtxPayShipForm(CreditPayShipForm):
    """Adds fields required by Prot/X to the Credit form."""
    
    card_holder = forms.CharField(max_length=75, required=False)
    month_start = forms.ChoiceField(choices=[(1, '--')]+MONTHS, required=False)
    year_start = forms.ChoiceField(required=False)
    issue_num = forms.CharField(max_length=2, required=False)
    
    def __init__(self, request, paymentmodule, *args, **kwargs):
        super(ProtxPayShipForm, self).__init__(request, paymentmodule, *args, **kwargs)
        cf = self.fields['card_holder']
        if (not cf.initial) or cf.initial == "":
            user = request.user
            if user and user.is_authenticated() and user.contact_set.count() > 0:
                cf.initial = self.tempContact.full_name
        self.requires_issue_number = REQUIRES_ISSUE_NUMBER
        self.fields['year_start'].choices = self.fields['year_expires'].choices

    def save(self, request, cart, contact, payment_module, data=None):
        """Save the order and the credit card details."""
        super(ProtxPayShipForm, self).save(request, cart, contact, payment_module)
        if data is None:
            data = self.cleaned_data 
        log.debug("data: %s", data)                       
        card_holder=data.get('card_holder', '')
        if not card_holder:
            card_holder = contact.full_name
        self.cc.card_holder = card_holder
        month_start = data.get('month_start', None)
        year_start = data.get('year_start', None)
        if month_start:
            try:
                month_start = int(month_start)
            except ValueError:
                log.warn("Could not parse month_start int from %s on order for order: %s", month_start, self.order)
                month_start = 1
                # TODO: raise some error to be caught by processor
        else:
            month_start=None
            
        if year_start:
            try:
                year_start = int(year_start)
            except ValueError:
                log.warn("Could not parse year_start int from %s on order for order: %s", year_start, self.order)
                year_start = 1
        else:
            year_start=None
        
        issue_num = data.get('issue_num', "")
        
        self.cc.start_month=month_start
        self.cc.start_year=year_start
        self.cc.issue_num=issue_num
        self.cc.save()

    def clean_card_holder(self):
        ch = self.cleaned_data['card_holder']
        if (not ch) or ch == "":
            fn = self.tempContact.full_name
            self.cleaned_data['card_holder'] = fn
            log.debug('Setting card_holder to contact full name: %s', fn)
        else:
            log.debug('Card holder OK')

    def clean_month_start(self):
        data = self.cleaned_data
        
        self._maybe_require(data, 'month_start', _('You must provide a starting month when using this type of card.'))

        if data['month_start']:
            try:
                v = int(self.cleaned_data['month_start'])
            except ValueError:
                raise forms.ValidationError(_("This must be a number"))
            
            if not v>0 and v<13:
                raise forms.ValidationError(_("Out of range, must be 1-12"))
            
    def clean_year_start(self):
        data = self.cleaned_data
        self._maybe_require(data, 'credit_type', _('You must provide a starting year when using this type of card.'))
        
        if data['year_start']:
            try:
                v = int(self.cleaned_data['year_start'])
            except ValueError:
                raise forms.ValidationError(_("This must be a number"))

            if not v>0 and v<13:
                raise forms.ValidationError(_("Out of range, must be 1-12"))

    def clean_issue_num(self):
        data = self.cleaned_data
        self._maybe_require(data, 'issue_num', _('You must provide an issue number when using this type of card.'))

    def _maybe_require(self, data, field, message):
        if data['credit_type'] in REQUIRES_ISSUE_NUMBER and not (data[field]):
            raise forms.ValidationError(message)
