import re

from django.utils.translation import ugettext as _

def validate(postcode):
    """
    Validates Australian postal codes.
    """
    postcode = postcode.strip()
    if postcode.isdigit():
        return postcode
    else:
        raise ValueError(_('Invalid Australian postal code'))
