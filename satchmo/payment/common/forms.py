from django import forms
from django.conf import settings
from django.template import loader
from django.template import RequestContext
from django.utils.translation import ugettext as _
from satchmo.configuration import config_value, config_choice_values
from satchmo.contact.forms import ContactInfoForm
from satchmo.contact.models import Contact
from satchmo.discount.models import Discount
from satchmo.discount.utils import find_best_auto_discount
from satchmo.l10n.utils import moneyfmt
from satchmo.payment.config import labelled_payment_choices
from satchmo.payment.models import CreditCardDetail
from satchmo.shipping.config import shipping_methods
from satchmo.shop.models import Cart
from satchmo.shop.views.utils import CreditCard
from satchmo.tax.templatetags.satchmo_tax import _get_taxprocessor
from satchmo.utils.dynamic import lookup_template
import calendar
import datetime
import sys

MONTHS = [(month,'%02d'%month) for month in range(1,13)]

def _get_shipping_choices(request, paymentmodule, cart, contact, default_view_tax=False):
    """Iterate through legal shipping modules, building the list for display to the user.
    
    Returns the shipping choices list, along with a dictionary of shipping choices, useful
    for building javascript that operates on shipping choices.
    """
    shipping_options = []
    shipping_dict = {}
    
    for method in shipping_methods():
        method.calculate(cart, contact)
        if method.valid():
            template = lookup_template(paymentmodule, 'shipping_options.html')
            t = loader.get_template(template)
            shipcost = method.cost()
            shipping_tax = None
            taxed_shipping_price = None
            if config_value('TAX','TAX_SHIPPING'):
                shipping_tax = config_value('TAX', 'TAX_CLASS')
                taxer = _get_taxprocessor(request)
                total = shipcost + taxer.by_price(shipping_tax, shipcost)
                taxed_shipping_price = moneyfmt(total)
            c = RequestContext(request, {
                'amount': shipcost,
                'description' : method.description(),
                'method' : method.method(),
                'expected_delivery' : method.expectedDelivery(),
                'default_view_tax' : default_view_tax,
                'shipping_tax': shipping_tax,
                'taxed_shipping_price': taxed_shipping_price})
            shipping_options.append((method.id, t.render(c)))
            shipping_dict[method.id] = shipcost
    
    return shipping_options, shipping_dict
     
class PaymentMethodForm(forms.Form):
    _choices = labelled_payment_choices()
    if len(_choices) > 0:
        
        if len(_choices) > 1:
            _paymentwidget = forms.RadioSelect
        else:
            _paymentwidget = forms.HiddenInput(attrs={'value' : _choices[0][0]})

        paymentmethod = forms.ChoiceField(label=_('Payment method'),
                                        choices=_choices,
                                        widget=_paymentwidget,
                                        required=True)

class PaymentContactInfoForm(ContactInfoForm):
    _choices = labelled_payment_choices()
    if len(_choices) > 0:
        if len(_choices) > 1:
            _paymentwidget = forms.RadioSelect
        else:
            _paymentwidget = forms.HiddenInput(attrs={'value' : _choices[0][0]})

        paymentmethod = forms.ChoiceField(label=_('Payment method'),
                                        choices=_choices,
                                        widget=_paymentwidget,
                                        required=True)

class SimplePayShipForm(forms.Form):
    shipping = forms.ChoiceField(widget=forms.RadioSelect(), required=False)
    discount = forms.CharField(max_length=30, required=False)

    def __init__(self, request, paymentmodule, *args, **kwargs):
        super(SimplePayShipForm, self).__init__(*args, **kwargs)
        
        try:
            self.tempCart = Cart.objects.from_request(request)
            if self.tempCart.numItems > 0:
                products = [item.product for item in self.tempCart.cartitem_set.all()]
                sale = find_best_auto_discount(products)
                if sale:
                    self.fields['discount'].initial = sale.code
            
        except Cart.DoesNotExist:
            self.tempCart = None
            
        try:
            self.tempContact = Contact.objects.from_request(request)
        except Contact.DoesNotExist:
            self.tempContact = None
            
        if kwargs.has_key('default_view_tax'):
            default_view_tax = kwargs['default_view_tax']
        else:
            default_view_tax = config_value('TAX', 'TAX_SHIPPING')
            
        shipping_choices, shipping_dict = _get_shipping_choices(request, paymentmodule, self.tempCart, self.tempContact, default_view_tax=default_view_tax)
        self.fields['shipping'].choices = shipping_choices
        self.shipping_dict = shipping_dict

    def clean_shipping(self):
        shipping = self.cleaned_data['shipping']
        if not shipping and self.tempCart.is_shippable:
            raise forms.ValidationError(_('This field is required.'))
        return shipping

    def clean_discount(self):
        """ Check if discount exists and is valid. """
        data = self.cleaned_data['discount']
        if data:
            try:
                discount = Discount.objects.get(code=data, active=True)
            except Discount.DoesNotExist:
                raise forms.ValidationError(_('Invalid discount.'))
            valid, msg = discount.isValid(self.tempCart)
            if not valid:
                raise forms.ValidationError(msg)
            # TODO: validate that it can work with these products
        return data

class CreditPayShipForm(SimplePayShipForm):
    credit_type = forms.ChoiceField()
    credit_number = forms.CharField(max_length=20)
    month_expires = forms.ChoiceField(choices=MONTHS)
    year_expires = forms.ChoiceField()
    ccv = forms.CharField(max_length=4, label='Sec code')

    def __init__(self, request, paymentmodule, *args, **kwargs):
        creditchoices = paymentmodule.CREDITCHOICES.choice_values
        super(CreditPayShipForm, self).__init__(request, paymentmodule, *args, **kwargs)

        self.fields['credit_type'].choices = creditchoices

        year_now = datetime.date.today().year
        self.fields['year_expires'].choices = [(year, year) for year in range(year_now, year_now+6)]

        self.tempCart = Cart.objects.from_request(request)
            
        try:
            self.tempContact = Contact.objects.from_request(request)
        except Contact.DoesNotExist:
            self.tempContact = None

        #shipping_choices, shipping_dict = _get_shipping_choices(paymentmodule, self.tempCart, self.tempContact)
        #self.fields['shipping'].choices = shipping_choices
        #self.shipping_dict = shipping_dict

    def clean_credit_number(self):
        """ Check if credit card is valid. """
        credit_number = self.cleaned_data['credit_number']
        card = CreditCard(credit_number, self.cleaned_data['credit_type'])
        results, msg = card.verifyCardTypeandNumber()
        if not results:
            raise forms.ValidationError(msg)
        return credit_number

    def clean_month_expires(self):
        return int(self.cleaned_data['month_expires'])

    def clean_year_expires(self):
        """ Check if credit card has expired. """
        month = self.cleaned_data['month_expires']
        year = int(self.cleaned_data['year_expires'])
        max_day = calendar.monthrange(year, month)[1]
        if datetime.date.today() > datetime.date(year=year, month=month, day=max_day):
            raise forms.ValidationError(_('Your card has expired.'))
        return year
    
    def clean_ccv(self):
        """ Validate a proper CCV is entered. Remember it can have a leading 0 so don't convert to int and return it"""
        try:
            check = int(self.cleaned_data['ccv'])
            return self.cleaned_data['ccv']
        except ValueError:
            raise forms.ValidationError(_('Invalid ccv.'))
            
    def save(self, orderpayment):
        """Save the credit card information for this orderpayment"""
        data = self.cleaned_data
        cc = CreditCardDetail(orderpayment=orderpayment,
            expire_month=data['month_expires'],
            expire_year=data['year_expires'],
            credit_type=data['credit_type'])
            
        cc.storeCC(data['credit_number'])
        cc.save()
        
        # set ccv into cache
        cc.ccv = data['ccv']
        
        return cc

