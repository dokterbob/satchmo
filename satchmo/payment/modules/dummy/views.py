"""Simple wrapper for standard checkout as implemented in satchmo.payment.common.views"""

from satchmo.configuration import config_get_group
from satchmo.payment.common.views import confirm, payship
    
dummy = config_get_group('PAYMENT_DUMMY')
    
def pay_ship_info(request):
    return payship.credit_pay_ship_info(request, dummy)
    
def confirm_info(request):
    return confirm.credit_confirm_info(request, dummy)


