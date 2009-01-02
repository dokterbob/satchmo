"""Simple wrapper for standard checkout as implemented in payment.views"""

from django.views.decorators.cache import never_cache
from livesettings import config_get_group
from payment.views import confirm, payship
    
cod = config_get_group('PAYMENT_COD')
    
def pay_ship_info(request):
    return payship.simple_pay_ship_info(request, config_get_group('PAYMENT_COD'), 'shop/checkout/cod/pay_ship.html')
pay_ship_info = never_cache(pay_ship_info)
    
def confirm_info(request):
    return confirm.credit_confirm_info(request, cod, template='shop/checkout/cod/confirm.html')
confirm_info = never_cache(confirm_info)

