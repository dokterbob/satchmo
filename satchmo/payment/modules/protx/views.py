"""Simple wrapper for standard checkout as implemented in satchmo.payment.common.views"""

from satchmo.payment.paymentsettings import PaymentSettings
from satchmo.payment.common.views import credit_confirm, credit_payship
    
def pay_ship_info(request):
    return credit_payship.pay_ship_info(request, PaymentSettings().PROTX)
    
def confirm_info(request):
    return credit_confirm.confirm_info(request, PaymentSettings().PROTX)

def confirm_secure3d(request):
    return credit_confirm.confirm_info(request, PaymentSettings().PROTX, secure3dstep=True)


