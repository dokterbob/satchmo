from decimal import Decimal, ROUND_HALF_UP, ROUND_DOWN, InvalidOperation, getcontext
from django import forms
from django.utils.translation import ugettext as _
from livesettings import config_value
import logging

log = logging.getLogger('satchmo_utils.numbers')

class RoundedDecimalField(forms.Field):
    def clean(self, value):
        """
        Normalize the field according to cart normalizing rules.
        """
        cartplaces = config_value('SHOP', 'CART_PRECISION')
        roundfactor = config_value('SHOP', 'CART_ROUNDING')    
        
        if not value or value == '':
            value = Decimal(0)

        try:
            value = round_decimal(val=value, places=cartplaces, roundfactor=roundfactor, normalize=True)
        except RoundedDecimalError:
            raise forms.ValidationError(_('%(value)s is not a valid number') % {'value' : value})

        return value

class PositiveRoundedDecimalField(RoundedDecimalField):
    """
    Normalize the field according to cart normalizing rules and force it to be positive.
    """
    def clean(self, value):
        value = super(PositiveRoundedDecimalField, self).clean(value)
        if value<0:
            log.debug('bad val: %s', value)
            raise forms.ValidationError(_('Please enter a positive number'))

        return value

class RoundedDecimalError:
    """
     General Purpose Error Handling used to handle error exceptions
     created in caller.
     Caller name and module taken from
     Activestate Recipe 66062: Determining Current Function Name
        # sys._getframe().f_code.co_name
        # sys._getframe().f_lineno
        # sys._getframe().f_code.co_filename
    """

    def __repr__(self):
        return "RoundedDecimalError - Partial Unit Rounding Error Exception Occured"

    def __init__(self, val='', id='', msg=''):
        import sys
        self.val = val
        self.id = id
        self.msg = msg
        self.caller_name = sys._getframe(1).f_code.co_name		#callers name
        self.caller_module = sys._getframe(1).f_code.co_filename	#module name of caller
        self.caller_lineno = sys._getframe(1).f_lineno		#line number of caller

def round_decimal(val='0', places=None, roundfactor='0', normalize=True):
    """
    PARTIAL UNIT ROUNDING DECIMAL
    Converts a valid float, integer, or string to a decimal number with a specified
    number of decimal places, performs "partial unit rounding", and decimal normalization.

    METHOD ARGUEMENTS:
    `val` The value to be converted and optionally formated to decimal.
    `places` The decimal precision is defined by integer "places" and
        must be <= the precision defined in the decimal.Decimal context.
    `roundfactor` (partial unit rounding factor) If purf is between -1 and 1, purf rounds up
        (positive purf value) or down (negative purf value) in factional "purf" increments.
    `normalize` If normalize is True (any value other than False), then rightmost zeros are truncated.
    """

    #-- Edit function arguments and set necessary defaults

    if str(normalize) == 'False': normalize = False     #Allow templates to submit False from filter

    try:
        roundfactor = Decimal(str(roundfactor))
    except (InvalidOperation, ValueError):
        raise RoundedDecimalError(val=roundfactor, id =1, msg="roundfactor - InvalidOperation or ValueError")  #reraise exception and return to caller
    if not (abs(roundfactor) >= 0 and abs(roundfactor) <= 1):
        raise RoundedDecimalError(val=roundfactor, id=2, msg="roundfactor - Out of Range - must be between -1 and +1")
    try:
        if places != None: places = int(places)
    except ValueError:
        raise RoundedDecimalError(val=places, id=3, msg='ValueError, Invalid Integer ')
    if places > getcontext().prec:
        raise RoundedDecimalError(val=places, id=4, msg='places Exceeds Decimal Context Precision')
    try:
        decval =Decimal(str(val))
    except (InvalidOperation, UnicodeEncodeError):
        raise RoundedDecimalError(val=val, id=5, msg='InvalidOperation - val cannot be converted to Decimal')
    
    #-- Round decimal number by the Partial Unit Rounding Factor
    if roundfactor and decval%roundfactor:
        if roundfactor < 0: roundby = 0
        else: roundby = (decval/abs(decval))*roundfactor	#change sign of roudby to decval
        decval=(decval//roundfactor*roundfactor)+roundby #round up or down by next roundfactor increment
    
    #-- Adjust number of decimal places if caller provided decimal places
    if places != None:
        decmask = '0.'.ljust(places+2,'0') #i.e. => '.00' if places eq 2
        decval=decval.quantize(Decimal(decmask), rounding=ROUND_DOWN)  #convert to Decimal and truncate to two decimals
    
    #-- normalize - strips the rightmost zeros... i.e. 2.0 => returns as 2
    if normalize:
        # if the number has no decimal portion return just the number with no decimal places
        # if the number has decimal places (i.e. 3.20), normalize the number (to 3.2)
        # This check is necesary because normalizing a number which trails in zeros (i.e. 200 or 200.00) normalizes to
        # scientific notation (2E+2)
        if decval==decval.to_integral():
            decval = decval.quantize(Decimal('1'))
        else:
            decval.normalize()
    
    return decval
    
def trunc_decimal(val, places):
    """Legacy compatibility, rounds the way the old satchmo 0.8.1 used to round."""
    if val is None or val == '':
       return val
    if val < 0:
        roundfactor = "-0.01"
    else:
        roundfactor = "0.01"
    return round_decimal(val=val, places=places, roundfactor=roundfactor, normalize=True)
