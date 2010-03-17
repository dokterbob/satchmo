from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils.translation import ugettext as _
from django.views.decorators.cache import never_cache
from satchmo_store.shop.models import Order
from satchmo_utils.views import bad_or_missing

def success(request):
    """
    The order has been succesfully processed.  This can be used to generate a receipt or some other confirmation
    """
    try:
        order = Order.objects.from_request(request)
    except Order.DoesNotExist:
        return bad_or_missing(request, _('Your order has already been processed.'))

    del request.session['orderID']
    return render_to_response('shop/checkout/success.html',
                              {'order': order},
                              context_instance=RequestContext(request))
success = never_cache(success)

def failure(request):
    return render_to_response(
        'shop/checkout/failure.html',
        {},
        context_instance=RequestContext(request)
    )
