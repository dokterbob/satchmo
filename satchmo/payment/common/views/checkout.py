from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils.translation import ugettext as _
from satchmo.shop.views.utils import bad_or_missing
from satchmo.contact.models import Order

def success(request):
    """
    The order has been succesfully processed.  This can be used to generate a receipt or some other confirmation
    """
    try:
        order = Order.objects.get(id=request.session['orderID'])
    except KeyError:
        return bad_or_missing(request, _('Your order has already been processed.'))
    del request.session['orderID']
    context = RequestContext(request, {'order': order})
    return render_to_response('checkout/success.html', context)