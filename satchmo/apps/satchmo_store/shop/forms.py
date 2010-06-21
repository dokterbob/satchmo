from decimal import Decimal
from django import forms
from django.contrib.sites.models import Site
from livesettings import config_value
from product.models import Product
from satchmo_store.shop.signals import satchmo_cart_details_query, satchmo_cart_add_complete
from satchmo_utils.numbers import RoundedDecimalError, round_decimal, PositiveRoundedDecimalField
import logging

log = logging.getLogger('shop.forms')

class MultipleProductForm(forms.Form):
    """A form used to add multiple products to the cart."""

    def __init__(self, *args, **kwargs):
        products = kwargs.pop('products', None)

        super(MultipleProductForm, self).__init__(*args, **kwargs)

        if products:
            products = [p for p in products if p.active]
        else:
            products = Product.objects.active_by_site()

        self.slugs = [p.slug for p in products]

        for product in products:
            kw = {
                'label' : product.name,
                'help_text' : product.description,
                'initial' : 0,
                'widget' : forms.TextInput(attrs={'class': 'text'}),
                'required' : False
            }

            qty = PositiveRoundedDecimalField(**kw)
            qty.product = product
            self.fields['qty__%s' % product.slug] = qty

    def save(self, cart, request):
        log.debug('saving');
        self.full_clean()
        cartplaces = config_value('SHOP', 'CART_PRECISION')
        roundfactor = config_value('SHOP', 'CART_ROUNDING')
        site = Site.objects.get_current()

        for name, value in self.cleaned_data.items():
            opt, key = name.split('__')
            log.debug('%s=%s', opt, key)

            quantity = 0
            product = None

            if opt=='qty':
                try:
                    quantity = round_decimal(value, places=cartplaces, roundfactor=roundfactor)
                except RoundedDecimalError:
                    quantity = 0

            if not key in self.slugs:
                log.debug('caught attempt to add product not in the form: %s', key)
            else:
                try:
                    product = Product.objects.get(slug=key, site=site)
                except Product.DoesNotExist:
                    log.debug('caught attempt to add an non-existent product, ignoring: %s', key)

            if product and quantity > Decimal('0'):
                log.debug('Adding %s=%s to cart from MultipleProductForm', key, value)
                details = []
                formdata = request.POST
                satchmo_cart_details_query.send(
                    cart,
                    product=product,
                    quantity=quantity,
                    details=details,
                    request=request,
                    form=formdata
                )
                added_item = cart.add_item(product, number_added=quantity, details=details)
                satchmo_cart_add_complete.send(cart, cart=cart, cartitem=added_item,
                    product=product, request=request, form=formdata)
