from django.views.decorators.cache import never_cache
from livesettings import config_get_group
from payment.views import confirm, payship
    
def pay_ship_info(request):
    return payship.credit_pay_ship_info(request, config_get_group('PAYMENT_AUTHORIZENET'))
pay_ship_info = never_cache(pay_ship_info)
    
def confirm_info(request):
    return confirm.credit_confirm_info(request, config_get_group('PAYMENT_AUTHORIZENET'))
confirm_info = never_cache(confirm_info)
