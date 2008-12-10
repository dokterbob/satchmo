from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils.translation import ugettext as _
from django.views.decorators.cache import never_cache
from satchmo.shop.views.utils import bad_or_missing
from satchmo.shop.models import Order

def success(request):
    """
    The order has been succesfully processed.  This can be used to generate a receipt or some other confirmation
    """
    try:
        order = Order.objects.from_request(request)
    except Order.DoesNotExist:
        return bad_or_missing(request, _('Your order has already been processed.'))
    
    # Added to track total sold for each product
    for item in order.orderitem_set.all():
        product = item.product
        product.total_sold += item.quantity
        product.items_in_stock -= item.quantity
        product.save()
        
    del request.session['orderID']
    context = RequestContext(request, {'order': order})
    return render_to_response('checkout/success.html', context)
success = never_cache(success)
