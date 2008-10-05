import re

from django.utils.translation import ugettext_lazy as _

US_POSTCODE_RE = re.compile(r'^\d{5}(?:-\d{4})?$')
def validate(postcode):
    if US_POSTCODE_RE.search(postcode):
        return postcode
    else:
        raise ValueError(_('Invalid ZIP code'))
