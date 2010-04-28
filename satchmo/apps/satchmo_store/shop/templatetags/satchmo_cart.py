from django import template
from livesettings import config_value
from l10n.utils import moneyfmt
from tax.templatetags.satchmo_tax import CartitemLineTaxedTotalNode, CartTaxedTotalNode
import logging

log = logging.getLogger('shop.templatetags.satchmo_cart')

register = template.Library()

class CartitemTotalNode(template.Node):
    """Show the total for the cartitem"""

    def __init__(self, cartitem, show_currency, show_tax):
        self.cartitem = template.Variable(cartitem)
        self.raw_cartitem = cartitem
        self.show_currency = template.Variable(show_currency)
        self.raw_currency = show_currency
        self.show_tax = template.Variable(show_tax)
        self.raw_tax = show_tax

    def render(self, context):

        try:
            show_tax = self.show_tax.resolve(context)
        except template.VariableDoesNotExist:
            show_tax = self.raw_tax

        if show_tax:
            tag = CartitemLineTaxedTotalNode(self.raw_cartitem, self.raw_currency)
            return tag.render(context)

        try:
            cartitem = self.cartitem.resolve(context)
        except template.VariableDoesNotExist:
            log.warn('Could not resolve template variable: %s', self.cartitem)
            return ''

        try:
            show_currency = self.show_currency.resolve(context)
        except template.VariableDoesNotExist:
            show_currency = self.raw_currency

        if show_currency:
            return moneyfmt(cartitem.line_total)
        else:
            return cartitem.line_total

def cartitem_custom_details(cartitem):
    is_custom = "CustomProduct" in cartitem.product.get_subtypes()

    return {
        'cartitem' : cartitem,
        'is_custom' : is_custom
    }

register.inclusion_tag("product/cart_detail_customproduct.html", takes_context=False)(cartitem_custom_details)

def cartitem_subscription_details(cartitem):
    log.debug('sub details')
    return {
        'cartitem' : cartitem,
        'is_subscription' : cartitem.product.is_subscription
    }

register.inclusion_tag("product/cart_detail_subscriptionproduct.html", takes_context=False)(cartitem_subscription_details)

def cartitem_total(parser, token):
    """Returns the line total for the cartitem, possibly with tax added.  If currency evaluates true,
    then return the total formatted through moneyfmt.

    Example::

        {% cartitem_total cartitem [show_tax] [currency] %}
    """

    tokens = token.contents.split()
    if len(tokens) < 2:
        raise template.TemplateSyntaxError, "'%s' tag requires a cartitem argument" % tokens[0]

    cartitem = tokens[1]

    if len(tokens) > 2:
        show_tax = tokens[2]
    else:
        show_tax = config_value('TAX', 'DEFAULT_VIEW_TAX')

    if len(tokens) >3:
        show_currency = tokens[3]
    else:
        show_currency = 'True'

    return CartitemTotalNode(cartitem, show_currency, show_tax)

cartitem_total = register.tag(cartitem_total)

class CartTotalNode(template.Node):
    """Show the total for the cart"""

    def __init__(self, cart, show_currency, show_tax, show_discount):
        self.cart = template.Variable(cart)
        self.raw_cart = cart
        self.show_currency = template.Variable(show_currency)
        self.raw_currency = show_currency
        self.show_tax = template.Variable(show_tax)
        self.raw_tax = show_tax
        self.show_discount = template.Variable(show_discount)
        self.raw_show_discount = show_discount

    def render(self, context):

        try:
            show_tax = self.show_tax.resolve(context)
        except template.VariableDoesNotExist:
            show_tax = self.raw_tax

        if show_tax:
            tag = CartTaxedTotalNode(self.raw_cart, self.raw_currency)
            return tag.render(context)

        try:
            cart = self.cart.resolve(context)
        except template.VariableDoesNotExist:
            log.warn('Could not resolve template variable: %s', self.cart)
            return ''

        try:
            show_currency = self.show_currency.resolve(context)
        except template.VariableDoesNotExist:
            show_currency = self.raw_currency

        try:
            show_discount = self.show_discount.resolve(context)
        except template.VariableDoesNotExist:
            show_discount = self.raw_show_discount

        if show_discount:
            total = cart.total_undiscounted
        else:
            total = cart.total

        if show_currency:
            return moneyfmt(cart.total)
        else:
            return cart.total

def cart_total(parser, token):
    """Returns the total for the cart, possibly with tax added.  If currency evaluates true,
    then return the total formatted through moneyfmt.

    Example::

        {% cart_total cart [show_tax] [currency] [discounted] %}
    """

    tokens = token.contents.split()
    if len(tokens) < 2:
        raise template.TemplateSyntaxError, "'%s' tag requires a cart argument" % tokens[0]

    cart = tokens[1]

    if len(tokens) > 2:
        show_tax = tokens[2]
    else:
        show_tax = config_value('TAX', 'DEFAULT_VIEW_TAX')

    if len(tokens) > 3:
        show_currency = tokens[3]
    else:
        show_currency = True

    if len(tokens) > 4:
        show_discount = tokens[4]
    else:
        show_discount = False

    return CartTotalNode(cart, show_currency, show_tax)

cart_total = register.tag(cart_total)
