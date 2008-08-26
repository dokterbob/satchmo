try:
    from decimal import Decimal
except:
    from django.utils._decimal import Decimal

import logging

from django.core import urlresolvers
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils.datastructures import MultiValueDictKeyError
from django.utils.safestring import mark_safe
from django.utils.simplejson.encoder import JSONEncoder
from django.utils.translation import ugettext as _

from satchmo.configuration import config_value
from satchmo.discount.utils import find_best_auto_discount
from satchmo.product.models import Product, OptionManager
from satchmo.product.views import find_product_template, optionset_from_post
from satchmo.shop import OutOfStockError
from satchmo.shop.models import Cart, CartItem, NullCart, NullCartItem
from satchmo.shop.signals import satchmo_cart_changed, satchmo_cart_add_complete, satchmo_cart_details_query
from satchmo.utils import trunc_decimal
from satchmo.shop.views.utils import bad_or_missing

log = logging.getLogger('shop.views.cart')

NOTSET = object()

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
        from satchmo.shop.models import Config
        config = Config.objects.get_current()
        if config.no_stock_checkout == False:
            stock = cartitem.product.items_in_stock
            log.debug('checking stock quantity.  Have %i, need %i', stock, qty)
            if stock < qty:
                return (False, cart, cartitem, _("Not enough items of '%s' in stock.") % cartitem.product.translated_name())
        cartitem.quantity = qty
        cartitem.save()

    satchmo_cart_changed.send(cart, cart=cart, request=request)
    return (True, cart, cartitem, "")

def display(request, cart=None, error_message='', default_view_tax=NOTSET):
    """Display the items in the cart."""

    if default_view_tax == NOTSET:
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
    return render_to_response('base_cart.html', context)

def add(request, id=0):
    """Add an item to the cart."""
    log.debug('FORM: %s', request.POST)
    formdata = request.POST.copy()
    productslug = None

    if formdata.has_key('productname'):
        productslug = formdata['productname']
    try:
        product, details = product_from_post(productslug, formdata)
        if not (product and product.active):
            return _product_error(request, product,
                _("That product is not available at the moment."))

    except (Product.DoesNotExist, MultiValueDictKeyError):
        log.debug("Could not find product: %s", productslug)
        return bad_or_missing(request, _('The product you have requested does not exist.'))

    try:
        quantity = int(formdata['quantity'])
    except ValueError:
        return _product_error(request, product,
            _("Please enter a whole number."))

    if quantity < 1:
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
    except OutOfStockError, os:
        if os.have == 0:
            msg = _("'%s' is out of stock.") % product.translated_name()
        else:
            msg = _("Only %(amount)i of '%(product)s' in stock.") % {'amount': os.have, 'product': product.translated_name()}
        return _product_error(request, product,msg)

    # got to here with no error, now send a signal so that listeners can also operate on this form.
    satchmo_cart_add_complete.send(cart, cart=cart, cartitem=added_item, product=product, request=request, form=formdata)
    satchmo_cart_changed.send(cart, cart=cart, request=request)

    url = urlresolvers.reverse('satchmo_cart')
    return HttpResponseRedirect(url)

def add_ajax(request, id=0, template="json.html"):
    data = {'errors': []}
    product = None
    formdata = request.POST.copy()
    if not formdata.has_key('productname'):
        data['errors'].append(('product', _('No product requested')))
    else:
        productslug = formdata['productname']
        log.debug('CART_AJAX: slug=%s', productslug)
        try:
            product, details = product_from_post(productslug, formdata)

        except Product.DoesNotExist:
            log.warn("Could not find product: %s", productslug)
            product = None

        if not product:
            data['errors'].append(('product', _('The product you have requested does not exist.')))

        else:
            if not product.active:
                data['errors'].append(('product', _('That product is not available at the moment.')))

            else:
                data['id'] = product.id
                data['name'] = product.translated_name()

                if not formdata.has_key('quantity'):
                    quantity = -1
                else:
                    quantity = formdata['quantity']

                try:
                    quantity = int(quantity)
                    if quantity < 0:
                        data['errors'].append(('quantity', _('Choose a quantity.')))

                except (TypeError, ValueError):
                    data['errors'].append(('quantity', _('Choose a whole number.')))

    tempCart = Cart.objects.from_request(request, create=True)

    if not data['errors']:
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
            added_item = tempCart.add_item(product, number_added=quantity)
            request.session['cart'] = tempCart.id
            data['results'] = _('Success')
            if added_item:
                # send a signal so that listeners can also operate on this form and item.
                satchmo_cart_add_complete.send(
                        cart,
                        cartitem=added_item,
                        product=product,
                        request=request,
                        form=formdata
                        )
        except OutOfStockError, oe:
            data['results'] = _('Error')
            if oe.have == 0:
                msg = _("'%s' is out of stock.") % product.translated_name()
            else:
                msg = _("Only %(amount)i of '%(product)s' in stock.") % {'amount': oe.have, 'product': product.translated_name()}
            data['errors'].append(('quantity', msg))
    else:
        data['results'] = _('Error')

    data['cart_count'] = tempCart.numItems

    encoded = JSONEncoder().encode(data)
    encoded = mark_safe(encoded)
    log.debug('CART AJAX: %s', data)

    satchmo_cart_changed.send(tempCart, cart=tempCart, request=request)
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
    cart_url = urlresolvers.reverse('satchmo_cart')
    
    if not request.POST:
        return HttpResponseRedirect(cart_url)
    
    success, cart, cartitem, errors = _set_quantity(request)
    if success:
        return HttpResponseRedirect(cart_url)
    else:
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
        if cart:
            carttotal = str(trunc_decimal(cart.total, 2))
            cartqty = cart.numItems
        else:
            carttotal = "0.00"
            cartqty = 0

        data['cart_total'] = carttotal
        data['cart_count'] = cartqty

        if cartitem:
            itemid = cartitem.id
            itemqty = cartitem.quantity
            price = str(trunc_decimal(cartitem.line_total, 2))
        else:
            itemid = -1
            itemqty = 0
            price = "0.00"

        data['item_id'] = itemid
        data['item_qty'] = itemqty
        data['item_price'] = price

    encoded = JSONEncoder().encode(data)
    encoded = mark_safe(encoded)
    return render_to_response(template, {'json': encoded})


def product_from_post(productslug, formdata):
    product = Product.objects.get_by_site(slug=productslug)
    log.debug('found product: %s', product)
    p_types = product.get_subtypes()
    details = []
    zero = Decimal("0.00")

    if 'ConfigurableProduct' in p_types:
        # This happens when productname cannot be updated by javascript.
        cp = product.configurableproduct
        chosenOptions = optionset_from_post(cp, formdata)
        product = cp.get_product_from_options(chosenOptions)

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
        chosenOptions = optionset_from_post(cp, formdata)
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
    template = find_product_template(product)
    context = RequestContext(request, {
        'product': product,
        'error_message': msg})
    return HttpResponse(template.render(context))

