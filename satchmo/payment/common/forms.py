from django import newforms as forms
from django.conf import settings
from django.template import Context
from django.template import loader
from django.utils.translation import ugettext as _
from satchmo.configuration import config_value
from satchmo.contact.forms import ContactInfoForm
from satchmo.contact.models import Contact
from satchmo.discount.models import Discount
from satchmo.payment.config import payment_choices
from satchmo.payment.urls import lookup_template
from satchmo.shop.models import Cart
from satchmo.shop.views.utils import CreditCard
from satchmo.shop.utils import load_module
import calendar
import datetime
import sys

def _get_shipping_choices(paymentmodule, cart, contact):
    """Iterate through legal shipping modules, building the list for display to the user.
    
    Returns the shipping choices list, along with a dictionary of shipping choices, useful
    for building javascript that operates on shipping choices.
    """
    shipping_options = []
    shipping_dict = {}
    
    for module in config_value('SHIPPING','MODULES'):
        #Create the list of information the user will see
        shipping_module = load_module(module)
        shipping_instance = shipping_module.Calc(cart, contact)
        if shipping_instance.valid():
            template = lookup_template(paymentmodule, 'shipping_options.html')
            t = loader.get_template(template)
            shipcost = shipping_instance.cost()
            c = Context({
                'amount': shipcost,
                'description' : shipping_instance.description(),
                'method' : shipping_instance.method(),
                'expected_delivery' : shipping_instance.expectedDelivery() })
            shipping_options.append((shipping_instance.id, t.render(c)))
            shipping_dict[shipping_instance.id] = shipcost
    
    return shipping_options, shipping_dict
    

class PaymentContactInfoForm(ContactInfoForm):
    _choices = payment_choices()
    if len(_choices) > 0:
        if len(_choices) > 1:
            _paymentwidget = forms.RadioSelect
        else:
            _paymentwidget = forms.HiddenInput(attrs={'value' : _choices[0][0]})

        paymentmethod = forms.ChoiceField(label=_('Payment method'),
                                        choices=_choices,
                                        widget=_paymentwidget,
                                        required=True)

class CreditPayShipForm(forms.Form):
    credit_type = forms.ChoiceField()
    credit_number = forms.CharField(max_length=20)
    month_expires = forms.ChoiceField(choices=[(month,month) for month in range(1,13)])
    year_expires = forms.ChoiceField()
    ccv = forms.IntegerField() # find min_length
    shipping = forms.ChoiceField(widget=forms.RadioSelect(), required=False)
    discount = forms.CharField(max_length=30, required=False)

    def __init__(self, request, paymentmodule, *args, **kwargs):
        creditchoices = paymentmodule.CREDITCHOICES.choice_values
        super(CreditPayShipForm, self).__init__(*args, **kwargs)

        self.fields['credit_type'].choices = creditchoices

        year_now = datetime.date.today().year
        self.fields['year_expires'].choices = [(year, year) for year in range(year_now, year_now+6)]

        self.tempCart = Cart.objects.get(id=request.session['cart'])
        self.tempContact = Contact.from_request(request)

        shipping_choices, shipping_dict = _get_shipping_choices(paymentmodule, self.tempCart, self.tempContact)
        self.fields['shipping'].choices = shipping_choices
        self.shipping_dict = shipping_dict

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

    def clean_shipping(self):
        shipping = self.cleaned_data['shipping']
        if not shipping and self.tempCart.is_shippable:
            raise forms.ValidationError(_('This field is required.'))
        return shipping

    def clean_discount(self):
        """ Check if discount exists and if it applies to these products """
        data = self.cleaned_data['discount']
        if data:
            discount = Discount.objects.filter(code=data).filter(active=True)
            if discount.count() == 0:
                raise forms.ValidationError(_('Invalid discount.'))
            valid, msg = discount[0].isValid(self.tempCart)
            if not valid:
                raise forms.ValidationError(msg)
        return data

class SimplePayShipForm(forms.Form):
    shipping = forms.ChoiceField(widget=forms.RadioSelect(), required=False)
    discount = forms.CharField(max_length=30, required=False)

    def __init__(self, request, paymentmodule, *args, **kwargs):
        super(SimplePayShipForm, self).__init__(*args, **kwargs)

        self.tempCart = Cart.objects.get(id=request.session['cart'])
        self.tempContact = Contact.from_request(request)
        shipping_choices, shipping_dict = _get_shipping_choices(paymentmodule, self.tempCart, self.tempContact)
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

