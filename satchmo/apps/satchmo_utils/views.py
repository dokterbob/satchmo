from django import http
from django.template import RequestContext
from django.template import loader
from django.utils.translation import ugettext as _

ccInfo = (
    #  type, prefix, length
    ( 'VISA', '4', 16),
    ( 'VISA', '4', 13),
    ( 'UKE', '417500', 16),
    ( 'UKE', '4917', 16),
    ( 'UKE', '4913', 16),
    ( 'SWITCH', '4903', 16),
    ( 'SWITCH', '4905', 16),
    ( 'SWITCH', '4911', 16),
    ( 'SWITCH', '4936', 16),
    ( 'SWITCH', '564182', 16),
    ( 'SWITCH', '633110', 16),
    ( 'SWITCH', '6333', 16),
    ( 'SWITCH', '6759', 16),
    ( 'SWITCH', '4903', 18),
    ( 'SWITCH', '4905', 18),
    ( 'SWITCH', '4911', 18),
    ( 'SWITCH', '4936', 18),
    ( 'SWITCH', '564182', 18),
    ( 'SWITCH', '633110', 18),
    ( 'SWITCH', '6333', 18),
    ( 'SWITCH', '6759', 18),
    ( 'SWITCH', '4903', 19),
    ( 'SWITCH', '4905', 19),
    ( 'SWITCH', '4911', 19),
    ( 'SWITCH', '4936', 19),
    ( 'SWITCH', '564182', 19),
    ( 'SWITCH', '633110', 19),
    ( 'SWITCH', '6333', 19),
    ( 'SWITCH', '6759', 19),
    ( 'SOLO', '6334', 16),
    ( 'SOLO', '6767', 16),  
    ( 'SOLO', '6334', 18),
    ( 'SOLO', '6767', 18),      
    ( 'SOLO', '6334', 19),
    ( 'SOLO', '6767', 19),    
    ( 'MAESTRO', '5020', 16),
    ( 'MAESTRO', '6', 16),
    ( 'MC', '51', 16),
    ( 'MC', '52', 16),
    ( 'MC', '53', 16),
    ( 'MC', '54', 16),
    ( 'MC', '55', 16),
    ( 'DISCOVER', '6011', 16),
    ( 'AMEX', '34', 15),
    ( 'AMEX', '37', 15),
    ( 'DC', '300', 14),
    ( 'DC', '301', 14),
    ( 'DC', '302', 14),
    ( 'DC', '303', 14),
    ( 'DC', '304', 14),
    ( 'DC', '305', 14),
    ( 'DC', '36', 14),
    ( 'DC', '38', 14),
    ( 'JCB', '3', 16),
    ( 'JCB', '2131', 15),
    ( 'JCB', '1800', 15),
)

class CreditCard(object):
    def __init__(self, number, cardtype):
        self.card_number = number
        self.card_type = cardtype

    def _verifyMod10(self, number):
        '''Check a credit card number for validity using the mod10 algorithm.'''
        double = 0
        sum = 0
        for i in range(len(number) - 1, -1, -1):
            for c in str((double + 1) * int(number[i])): sum = sum + int(c)
            double = (double + 1) % 2
        return ((sum % 10) == 0)

    def _stripCardNum(self, card):
        '''Return card number with all non-digits stripped.  '''
        import re
        return re.sub(r'[^0-9]', '', self.card_number)

    def verifyCardNumber(self):
        '''Return card type string if legal, None otherwise.
        Check the card number and return a string representing the card type if
        it could be a valid card number.

        RETURNS: (String) Credit card type string if legal.(None) if invalid.
        '''
        s = self._stripCardNum(self.card_number)
        if self._verifyMod10(s):
            return self.card_type
        return None

    def verifyCardTypeandNumber(self):
        card_check_type = self.verifyCardNumber()
        if card_check_type:
            if card_check_type == self.card_type:
                return (True, None)
            else:
                return (False, _("Card type does not match card number."))
        else:
            return (False, _("Invalid credit card number."))

def bad_or_missing(request, msg):
    """
    Return an HTTP 404 response for a date request that cannot possibly exist.
    The 'msg' parameter gives the message for the main panel on the page.
    """
    template = loader.get_template('shop/404.html')
    context = RequestContext(request, {'message': msg})
    return http.HttpResponseNotFound(template.render(context))
