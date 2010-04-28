from decimal import Decimal
from django.core import urlresolvers
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.shortcuts import render_to_response
from django.template import RequestContext, loader
from django.utils.datastructures import MultiValueDictKeyError
from django.utils.safestring import mark_safe
from django.utils import simplejson
from django.utils.translation import ugettext as _
from django.views.decorators.cache import never_cache
from livesettings import config_value
from product.models import Product, OptionManager
from product.utils import find_best_auto_discount
from product.views import optionids_from_post
from satchmo_store.shop import forms
from satchmo_store.shop.exceptions import CartAddProhibited
from satchmo_store.shop.models import Cart, CartItem, NullCart, NullCartItem
from satchmo_store.shop.signals import satchmo_cart_changed, satchmo_cart_add_complete, satchmo_cart_details_query
from satchmo_utils.numbers import RoundedDecimalError, round_decimal
from satchmo_utils.views import bad_or_missing
import logging

try:
    from django.utils.simplejson.encoder import JSONEncoder
except ImportError:
    from simplejson.encoder import JSONEncoder

log = logging.getLogger('shop.views.cart')


def _json_response(data, error=False, template="shop/json.html"):
    response = HttpResponse(loader.render_to_string(template, 
        {'json':mark_safe(simplejson.dumps(data))}), mimetype='application/javascript')
    
    if error:
        response.status_code = 400
    
    return response

def decimal_too_big(quantity):
    """
    Helper to make sure the decimal number isn't too big to process.
    This does not validate whether or not the decimal is valid just that a
    Decimal is too large.
    """
    try:
        if Decimal(quantity) > Decimal("100000000000"):
            return True
        else:
            return False
    except:
        return False


def _set_quantity(request, force_delete=False):
    """Set the quantity for a specific cartitem.
    Checks to make sure the item is actually in the user's cart.
    """
    cart = Cart.objects.from_request(request, create=False)
    if isinstance(cart, NullCart):
        return (False, None, None, _("No cart to update."))

    cartplaces = config_value('SHOP', 'CART_PRECISION')

    if decimal_too_big(request.POST.get('quantity', 0)):
        return (False,cart,None,_("Bad quantity."))

    if force_delete:
        qty = Decimal('0')
    else:
        try:
            roundfactor = config_value('SHOP', 'CART_ROUNDING')
            qty = round_decimal(request.POST.get('quantity', 0), places=cartplaces, roundfactor=roundfactor, normalize=True)
        except RoundedDecimalError, P:
            return (False, cart, None, _("Bad quantity."))

        if qty < Decimal('0'):
            qty = Decimal('0')

    try:
        itemid = int(request.POST.get('cartitem'))
    except (TypeError, ValueError):
        return (False, cart, None, _("Bad item number."))

    try:
        cartitem = CartItem.objects.get(pk=itemid, cart=cart)
    except CartItem.DoesNotExist:
        return (False, cart, None, _("No such item in your cart."))

    if qty == Decimal('0'):
        cartitem.delete()
        cartitem = NullCartItem(itemid)
    else:
        from satchmo_store.shop.models import Config
        config = Config.objects.get_current()
        if config_value('PRODUCT','NO_STOCK_CHECKOUT') == False:
            stock = cartitem.product.items_in_stock
            log.debug('checking stock quantity.  Have %d, need %d', stock, qty)
            if stock < qty:
                return (False, cart, cartitem, _("Not enough items of '%s' in stock.") % cartitem.product.translated_name())

        cartitem.quantity = round_decimal(qty, places=cartplaces)
        cartitem.save()

    satchmo_cart_changed.send(cart, cart=cart, request=request)
    return (True, cart, cartitem, "")

def display(request, cart=None, error_message='', default_view_tax=None):
    """Display the items in the cart."""

    if default_view_tax is None:
        default_view_tax = config_value('TAX', 'DEFAULT_VIEW_TAX')

    if not cart:
        cart = Cart.objects.from_request(request)

    if cart.numItems > 0:
        products = [item.product for item in cart.cartitem_set.all()]
        sale = find_best_auto_discount(products)
    else:
        sale = None

    context = RequestContext(request, {
        'cart': cart,
        'error_message': error_message,
        'default_view_tax' : default_view_tax,
        'sale' : sale,
        })
    return render_to_response('shop/cart.html', context_instance=context)

display = never_cache(display)

def add(request, id=0, redirect_to='satchmo_cart'):
    """Add an item to the cart."""
    log.debug('FORM: %s', request.POST)
    formdata = request.POST.copy()
    productslug = None

    cartplaces = config_value('SHOP', 'CART_PRECISION')
    roundfactor = config_value('SHOP', 'CART_ROUNDING')


    if formdata.has_key('productname'):
        productslug = formdata['productname']
    try:
        product, details = product_from_post(productslug, formdata)

        if not (product and product.active):
            log.debug("product %s is not active" % productslug)
            return bad_or_missing(request, _("That product is not available at the moment."))
        else:
            log.debug("product %s is active" % productslug)

    except (Product.DoesNotExist, MultiValueDictKeyError):
        log.debug("Could not find product: %s", productslug)
        return bad_or_missing(request, _('The product you have requested does not exist.'))

    # First we validate that the number isn't too big.
    if decimal_too_big(formdata['quantity']):
        return _product_error(request, product, _("Please enter a smaller number."))

    # Then we validate that we can round it appropriately.
    try:
        quantity = round_decimal(formdata['quantity'], places=cartplaces, roundfactor=roundfactor)
    except RoundedDecimalError, P:
        return _product_error(request, product,
            _("Invalid quantity."))

    if quantity <= Decimal('0'):
        return _product_error(request, product,
            _("Please enter a positive number."))

    cart = Cart.objects.from_request(request, create=True)
    # send a signal so that listeners can update product details before we add it to the cart.
    satchmo_cart_details_query.send(
            cart,
            product=product,
            quantity=quantity,
            details=details,
            request=request,
            form=formdata
            )
    try:
        added_item = cart.add_item(product, number_added=quantity, details=details)

    except CartAddProhibited, cap:
        return _product_error(request, product, cap.message)

    # got to here with no error, now send a signal so that listeners can also operate on this form.
    satchmo_cart_add_complete.send(cart, cart=cart, cartitem=added_item, product=product, request=request, form=formdata)
    satchmo_cart_changed.send(cart, cart=cart, request=request)

    if request.is_ajax():
        data = {}
        data['id'] = product.id
        data['name'] = product.translated_name()
        data['cart_count'] = str(round_decimal(cart.numItems, 2))
        data['cart_total'] = str(cart.total)
        # Legacy result, for now
        data['results'] = _("Success")
        log.debug('CART AJAX: %s', data)
        
        return _json_response(data)
    else:
        url = urlresolvers.reverse(redirect_to)
        return HttpResponseRedirect(url)

def add_ajax(request, id=0, template="shop/json.html"):
    # Allow for legacy apps to still use this url
    if not request.META.has_key('HTTP_X_REQUESTED_WITH'):
        request.META['HTTP_X_REQUESTED_WITH'] = 'XMLHttpRequest'
        
    return add(request, id)

def add_multiple(request, redirect_to='satchmo_cart', products=None, template="shop/multiple_product_form.html"):
    """Add multiple items to the cart.
    """
    if request.method == "POST":
        log.debug('FORM: %s', request.POST)
        formdata = request.POST.copy()
        form = forms.MultipleProductForm(formdata, products=products)

        if form.is_valid():
            cart = Cart.objects.from_request(request, create=True)
            form.save(cart, request)
            satchmo_cart_changed.send(cart, cart=cart, request=request)

            url = urlresolvers.reverse(redirect_to)
            return HttpResponseRedirect(url)
    else:
        form = forms.MultipleProductForm(products=products)

    return render_to_response(template, context_instance=RequestContext(request, {'form' : form}))

def agree_terms(request):
    """Agree to terms"""
    if request.method == "POST":
        if request.POST.get('agree_terms', False):
            url = urlresolvers.reverse('satchmo_checkout-step1')
            return HttpResponseRedirect(url)

    return display(request, error_message=_('You must accept the terms and conditions.'))

def remove(request):
    """Remove an item from the cart."""
    if not request.POST:
        # Should be a POST request
        return bad_or_missing(request, "Please use a POST request")

    success, cart, cartitem, errors = _set_quantity(request, force_delete=True)
    
    if request.is_ajax():
        if errors:
            return _json_response({'errors': errors, 'results': _("Error")}, True)
        else:
            return _json_response({
                'cart_total': str(cart.total),
                'cart_count': str(cart.numItems),
                'item_id': cartitem.id,
                'results': success, # Legacy
            })
    else:
        if errors:
            return display(request, cart=cart, error_message=errors)
        else:
            url = urlresolvers.reverse('satchmo_cart')
            return HttpResponseRedirect(url)

def remove_ajax(request, template="shop/json.html"):
    """Remove an item from the cart. Returning JSON formatted results."""
    # Allow for legacy apps to still use this url
    if not request.META.has_key('HTTP_X_REQUESTED_WITH'):
        request.META['HTTP_X_REQUESTED_WITH'] = 'XMLHttpRequest'
        
    return remove(request)

def set_quantity(request):
    """Set the quantity for a cart item.

    Intended to be called via the cart itself, returning to the cart after done.
    """
    cart_url = urlresolvers.reverse('satchmo_cart')

    if not request.POST:
        return HttpResponseRedirect(cart_url)

    success, cart, cartitem, errors = _set_quantity(request)
            
    if request.is_ajax():
        if errors:
            return _json_response({'errors': errors, 'results': _("Error")}, True)
        else:
            return _json_response({
                'item_id': cartitem.id,
                'item_qty': str(cartitem.quantity) or "0",
                'item_price': str(cartitem.line_total) or "0.00",
                'cart_total': str(cart.total) or "0.00",
                'cart_count': str(cart.numItems) or '0',
            })
        
    else:
        if success:
            return HttpResponseRedirect(cart_url)
        else:
            return display(request, cart = cart, error_message = errors)
        
        
def set_quantity_ajax(request, template="shop/json.html"):
    """Set the quantity for a cart item, returning results formatted for handling by script.
    Kept for legacy apps.
    """
    if not request.META.has_key('HTTP_X_REQUESTED_WITH'):
        request.META['HTTP_X_REQUESTED_WITH'] = 'XMLHttpRequest'
        
    return set_quantity(request)

def product_from_post(productslug, formdata):
    product = Product.objects.get_by_site(slug=productslug)
    log.debug('found product: %s', product)
    p_types = product.get_subtypes()
    details = []
    zero = Decimal("0.00")

    if 'ConfigurableProduct' in p_types:
        # This happens when productname cannot be updated by javascript.
        cp = product.configurableproduct
        chosenOptions = optionids_from_post(cp, formdata)
        optproduct = cp.get_product_from_options(chosenOptions)
        if not optproduct:
            log.debug('Could not fully configure a ConfigurableProduct [%s] with [%s]', product, chosenOptions)
            raise Product.DoesNotExist()
        else:
            product = optproduct

    if 'CustomProduct' in p_types:
        cp = product.customproduct
        for customfield in cp.custom_text_fields.all():
            if customfield.price_change is not None:
                price_change = customfield.price_change
            else:
                price_change = zero
            data = { 'name' : customfield.translated_name(),
                     'value' : formdata["custom_%s" % customfield.slug],
                     'sort_order': customfield.sort_order,
                     'price_change': price_change }
            details.append(data)
            data = {}
        chosenOptions = optionids_from_post(cp, formdata)
        manager = OptionManager()
        for choice in chosenOptions:
            result = manager.from_unique_id(choice)
            if result.price_change is not None:
                price_change = result.price_change
            else:
                price_change = zero
            data = { 'name': unicode(result.option_group),
                      'value': unicode(result.translated_name()),
                      'sort_order': result.sort_order,
                      'price_change': price_change
            }
            details.append(data)
            data = {}

    if 'GiftCertificateProduct' in p_types:
        ix = 0
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

    return product, details

def _product_error(request, product, msg):
    request.session['ERRORS'] = msg
    log.debug('Product Error: %s', msg)
    
    if request.is_ajax():
        return _json_response({'errors': [msg,]}, error=True)
    else:
        request.session['ERRORS'] = msg
        return HttpResponseRedirect(product.get_absolute_url())

