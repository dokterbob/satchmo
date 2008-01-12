from decimal import Decimal
from django.core import urlresolvers
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils.datastructures import MultiValueDictKeyError
from django.utils.safestring import mark_safe
from django.utils.simplejson.encoder import JSONEncoder
from django.utils.translation import ugettext as _
from satchmo.configuration import config_value
from satchmo.product.models import Product, OptionManager
from satchmo.product.views import find_product_template, optionset_from_post
from satchmo.shop.models import Cart, CartItem, NullCart
from satchmo.shop.views.utils import bad_or_missing
import logging

log = logging.getLogger('shop.views.cart')

NOTSET = object()

class NullCartItem(object):
    def __init__(self, itemid):
        self.id = itemid
        self.quantity = 0
        self.line_total = 0

def _set_quantity(request, force_delete=False):
    """Set the quantity for a specific cartitem.
    Checks to make sure the item is actually in the user's cart.
    """
    cart = Cart.objects.from_request(request, create=False)
    if isinstance(cart, NullCart):
        return (False, None, None, _("No cart to update."))

    if force_delete:
        qty = 0
    else:
        try:
            qty = int(request.POST.get('quantity'))
        except (TypeError, ValueError):
            return (False, cart, None, _("Bad quantity."))
        if qty < 0:
            qty = 0

    try:
        itemid = int(request.POST.get('cartitem'))
    except (TypeError, ValueError):
        return (False, cart, None, _("Bad item number."))

    try:
        cartitem = CartItem.objects.get(pk=itemid, cart=cart)
    except CartItem.DoesNotExist:
        return (False, cart, None, _("No such item in your cart."))

    if qty == 0:
        cartitem.delete()
        cartitem = NullCartItem(itemid)
    else:
        cartitem.quantity = qty
        cartitem.save()

    return (True, cart, cartitem, "")

def display(request, cart=None, error_message='', default_view_tax=NOTSET):
    """Display the items in the cart."""
    
    if default_view_tax == NOTSET:
        default_view_tax = config_value('TAX', 'DEFAULT_VIEW_TAX')
            
    if not cart:
        cart = Cart.objects.from_request(request)
                
    context = RequestContext(request, {
        'cart': cart,
        'error_message': error_message,
        'default_view_tax' : default_view_tax,
        })
    return render_to_response('base_cart.html', context)

def add(request, id=0):
    """Add an item to the cart."""
    #TODO: Error checking for invalid combos
    log.debug('FORM: %s', request.POST)
    formdata = request.POST.copy()
    productslug = formdata['productname']
    try:
        product = Product.objects.get(slug=productslug)
        log.debug('found product: %s', product)
        p_types = product.get_subtypes()
        details = []

        if 'ConfigurableProduct' in p_types:
            # This happens when productname cannot be updated by javascript.
            cp = product.configurableproduct
            chosenOptions = optionset_from_post(cp, formdata)
            product = cp.get_product_from_options(chosenOptions)

        if 'CustomProduct' in p_types:
            cp = product.customproduct
            for customfield in cp.custom_text_fields.all():
                data = { 'name' : customfield.translated_name(),
                         'value' : formdata["custom_%s" % customfield.slug],
                         'sort_order': customfield.sort_order,
                         'price_change': customfield.price_change }
                details.append(data)
                data = {}
            chosenOptions = optionset_from_post(cp, formdata)
            manager = OptionManager()
            for choice in chosenOptions:
                result = manager.from_unique_id(choice)
                data = { 'name': result.optionGroup,
                          'value': result.translated_name(),
                          'sort_order': result.displayOrder,
                          'price_change': result.price_change
                }
                details.append(data)
                data = {}
                
        if 'GiftCertificateProduct' in p_types:
            ix = 0
            zero = Decimal("0.00")
            for field in ('email', 'message'):
                data = {
                    'name' : field,
                    'value' : formdata.get("custom_%s" % field, ""),
                    'sort_order' : ix,
                    'price_change' : zero,
                }
                ix += 1
                details.append(data)
            log.debug("Gift Certificate details: %s", details)
            data = {}

        template = find_product_template(product)
    except (Product.DoesNotExist, MultiValueDictKeyError):
        log.debug("Could not find product: %s", productslug)
        return bad_or_missing(request, _('The product you have requested does not exist.'))

    try:
        quantity = int(formdata['quantity'])
    except ValueError:
        context = RequestContext(request, {
            'product': product,
            'error_message': _("Please enter a whole number.")})

        return HttpResponse(template.render(context))

    if quantity < 1:
        context = RequestContext(request, {
            'product': product,
            'error_message': _("Please enter a positive number.")})
        return HttpResponse(template.render(context))

    cart = Cart.objects.from_request(request, create=True)
    cart.add_item(product, number_added=quantity, details=details)

    url = urlresolvers.reverse('satchmo_cart')
    return HttpResponseRedirect(url)

def add_ajax(request, id=0, template="json.html"):
    data = {'errors': []}
    product = None
    productname = request.POST['productname']
    log.debug('CART_AJAX: slug=%s', productname)
    try:
        product = Product.objects.get(slug=request.POST['productname'])
        if 'ConfigurableProduct' in product.get_subtypes():
            log.debug('Got a configurable product, trying by option')
            # This happens when productname cannot be updated by javascript.
            cp = product.configurableproduct
            chosenOptions = optionset_from_post(cp, request.POST)
            product = cp.get_product_from_options(chosenOptions)
    except Product.DoesNotExist:
        log.warn("Could not find product: %s", productname)
        product = None

    if not product:
        data['errors'].append(('product', _('The product you have requested does not exist.')))

    else:
        data['id'] = product.id
        data['name'] = product.translated_name()

        try:
            quantity = int(request.POST['quantity'])
            if quantity < 0:
                data['errors'].append(('quantity', _('Choose a quantity.')))

        except ValueError:
            data['errors'].append(('quantity', _('Choose a whole number.')))

    tempCart = Cart.objects.from_request(request, create=True)

    if not data['errors']:
        tempCart.add_item(product, number_added=quantity)
        request.session['cart'] = tempCart.id
        data['results'] = _('Success')
    else:
        data['results'] = _('Error')

    data['cart_count'] = tempCart.numItems

    encoded = JSONEncoder().encode(data)
    encoded = mark_safe(encoded)
    log.debug('CART AJAX: %s', data)

    return render_to_response(template, {'json' : encoded})

def agree_terms(request):
    """Agree to terms"""
    if request.method == "POST":
        if request.POST.get('agree_terms', False):
            url = urlresolvers.reverse('satchmo_checkout-step1')
            return HttpResponseRedirect(url)

    return display(request, error_message=_('You must accept the terms and conditions.'))

def remove(request):
    """Remove an item from the cart."""
    success, cart, cartitem, errors = _set_quantity(request, force_delete=True)
    if errors:
        return display(request, cart=cart, error_message=errors)
    else:
        url = urlresolvers.reverse('satchmo_cart')
        return HttpResponseRedirect(url)

def remove_ajax(request, template="json.html"):
    """Remove an item from the cart. Returning JSON formatted results."""
    data = {}
    if not request.POST:
        data['results'] = False
        data['errors'] = _('Internal error: please submit as a POST')

    else:
        success, cart, cartitem, errors = _set_quantity(request, force_delete=True)

        data['results'] = success
        data['errors'] = errors

        # note we have to convert Decimals to strings, since simplejson doesn't know about Decimals
        if cart and cartitem:
            data['cart_total'] = str(cart.total)
            data['cart_count'] = cart.numItems
            data['item_id'] = cartitem.id

        return render_to_response(template, {'json': JSONEncoder().encode(data)})

def set_quantity(request):
    """Set the quantity for a cart item.

    Intended to be called via the cart itself, returning to the cart after done.
    """
    if not request.POST:
        url = urlresolvers.reverse('satchmo_cart')
        return HttpResponseRedirect(url)

    success, cart, cartitem, errors = _set_quantity(request)
    return display(request, cart = cart, error_message = errors)

def set_quantity_ajax(request, template="json.html"):
    """Set the quantity for a cart item, returning results formatted for handling by script.
    """
    data = {}
    if not request.POST:
        data['results'] = False
        data['errors'] = _('Internal error: please submit as a POST')

    else:
        success, cart, cartitem, errors = _set_quantity(request)

        data['results'] = success
        data['errors'] = errors

        # note we have to convert Decimals to strings, since simplejson doesn't know about Decimals
        if cart and cartitem:
            data['cart_total'] = str(cart.total)
            data['cart_count'] = cart.numItems
            data['item_id'] = cartitem.id
            data['item_qty'] = cartitem.quantity
            data['item_price'] = str(cartitem.line_total)

    encoded = JSONEncoder().encode(data)
    encoded = mark_safe(encoded)
    return render_to_response(template, {'json': encoded})

