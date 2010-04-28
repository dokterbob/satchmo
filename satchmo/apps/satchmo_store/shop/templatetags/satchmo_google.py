from django.template import Library
from django.conf import settings
from satchmo_store.contact.models import Contact
from livesettings import config_value
import sys

register = Library()

def show_tracker(secure=False):
    """
    Output the google tracker code.
    """
    return({"GOOGLE_CODE": config_value('GOOGLE', 'ANALYTICS_CODE'),
            "secure" : secure})

register.inclusion_tag("shop/google-analytics/tracker.html")(show_tracker)

def show_receipt(context):
    """
    Output our receipt in the format that Google Analytics needs.
    """
    return({'Store': settings.SITE_NAME,
            'order': context['order']})

register.inclusion_tag("shop/google-analytics/receipt.html", takes_context=True)(show_receipt)

def google_track_signup(context):
    """
    Output a a new user signup in the format that Google Analytics needs.
    """
    request = context['request']
    try:
        contact = Contact.objects.from_request(request, create=False)
    except Contact.DoesNotExist:
        contact = None

    return({'contact' : contact})

register.inclusion_tag("shop/google-analytics/signup.html", takes_context=True)(google_track_signup)

def google_adwords_sale(context):
    """
    Output our receipt in the format that Google Adwords needs.
    """
    order = context['order']
    try:
        request = context['request']
    except KeyError:
        print >> sys.stderr, "Template satchmo.show.templatetags.google.google_adwords_sale couldn't get the request from the context.  Are you missing the request context_processor?"
        return ""

    secure = request.is_secure()
    try:
        language_code = request.LANGUAGE_CODE
    except KeyError:
        language_code = settings.LANGUAGE_CODE

    return({"GOOGLE_ADWORDS_ID": config_value('GOOGLE', 'ADWORDS_ID'),
            'Store': settings.SITE_NAME,
            'value': order.total,
            'label': 'purchase',
            'secure' : secure,
            'language_code' : language_code})

register.inclusion_tag("shop/google-analytics/adwords_conversion.html", takes_context=True)(google_adwords_sale)

def google_adwords_signup(context):
    """
    Output signup info in the format that Google adwords needs.
    """
    request = context['request']
    try:
        request = context['request']
    except KeyError:
        print >> sys.stderr, "Template satchmo.show.templatetags.google.google_adwords_sale couldn't get the request from the context.  Are you missing the request context_processor?"
        return ""

    secure = request.is_secure()
    try:
        language_code = request.LANGUAGE_CODE
    except AttributeError:
        language_code = settings.LANGUAGE_CODE

    return({"GOOGLE_ADWORDS_ID": config_value('GOOGLE', 'ADWORDS_ID'),
            'Store': settings.SITE_NAME,
            'value': 1,
            'label': 'signup',
            'secure' : secure,
            'language_code' : language_code})

register.inclusion_tag("shop/google-analytics/adwords_conversion.html", takes_context=True)(google_adwords_signup)
