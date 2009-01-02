"""
Canadian postal code validation. The structure of the codes is at:

http://www.canadapost.ca/tools/pg/manual/pgaddress-e.asp#1380891

"""
import re

from django.utils.translation import ugettext_lazy as _

CA_POSTCODE_RE = re.compile(r'^(?P<FSA>[ABCEGHJKLMNPRSTVXYZ]\d[A-Z])\s*(?P<LDU>\d[A-Z]\d)$')
def validate(postcode):
    postcode = postcode.upper()
    m = CA_POSTCODE_RE.match(postcode)
    if m:
        return m.group('FSA') + m.group('LDU')
    else:
        raise ValueError(_('Invalid postal code for Canada'))
