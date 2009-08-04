from django import template
from django.utils import translation
from livesettings import config_get_group
from payment.modules.google import CHECKOUT_BUTTON_SIZES
from django.utils.http import urlencode

register = template.Library()

def _truefalse(val, t="1", f="0"):
    if val:
        return t
    else:
        return f

def checkout_image_url(merchid, imgsize, locale, transparent=False, disabled=False):
    payment_module = config_get_group('PAYMENT_GOOGLE')
    dimensions = CHECKOUT_BUTTON_SIZES[imgsize]
    return ("%s?%s" % (
        payment_module.CHECKOUT_BUTTON_URL,
        urlencode((('merchant_id', merchid),
                  ('w', dimensions[0]),
                  ('h', dimensions[1]),
                  ('style', _truefalse(transparent, t="trans", f="white")),
                  ('variant', _truefalse(disabled, t="disabled", f="text")),
                  ('loc', locale)))))


class GoogleCheckoutImageUrlNode(template.Node):
    def __init__(self, merchid, imgsize, transparent, disabled):
        self.merchid = merchid
        self.imgsize = imgsize
        self.transparent = transparent
        self.disabled = disabled

    def render(self, context):
        lang = translation.get_language()
        locale = translation.to_locale(lang)

        return checkout_image_url(self.merchid, self.imgsize, locale, transparent=self.transparent, disabled=self.disabled)


def google_checkout_image_url(parser, token):
    """
    Render the url for a google checkout image.

    Sample usage::

      {% google_checkout_image_url [imagesize] ['transparent'] ['disabled'] %}

    """
    args = token.split_contents()
    payment_module = config_get_group('PAYMENT_GOOGLE')
    merchid = payment_module.MERCHANT_ID
    sizes = CHECKOUT_BUTTON_SIZES.keys()

    imgsize = "MEDIUM"
    transparent = False
    disabled = False
    locale = None

    for arg in args[1:]:
        k = arg.upper()
        if k == 'TRANSPARENT':
            transparent = True
        elif k == 'DISABLED':
            disabled = True
        else:
            if k in sizes:
                imgsize = k
            else:
                raise template.TemplateSyntaxError("%r tag got an unexpected argument.  Perhaps a bad size?  Didn't know: %s" % (args[0], arg))
                
    return GoogleCheckoutImageUrlNode(merchid, imgsize, transparent, disabled)

register.tag(google_checkout_image_url)
