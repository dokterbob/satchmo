"""Simple wrapper for standard checkout as implemented in satchmo.payment.common.views"""

from satchmo.configuration import config_get_group
from satchmo.payment.common.views import confirm, payship
    
cod = config_get_group('PAYMENT_COD')
    
def pay_ship_info(request):
    return payship.simple_pay_ship_info(request, config_get_group('PAYMENT_COD'), 'checkout/cod/pay_ship.html')
    
def confirm_info(request):
    return confirm.credit_confirm_info(request, cod, 'checkout/cod/confirm.html')


