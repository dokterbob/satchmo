from decimal import Decimal
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils.translation import ugettext_lazy as _
from satchmo.contact.models import OrderItem
from satchmo.payment.common.views import common_contact
from satchmo.shop.views.utils import bad_or_missing
import django.newforms as forms
import logging

log = logging.getLogger('payment.views')

class CustomChargeForm(forms.Form):
    orderitem = forms.IntegerField(required=True, widget=forms.HiddenInput())
    amount = forms.DecimalField(label=_('New price'), required=False)
    shipping = forms.DecimalField(label=_('Shipping adjustment'), required=False)
    notes = forms.CharField(_("Notes"), required=False, initial="Your custom item is ready.")

def contact_info(request):
    return common_contact.contact_info(request)

def charge_remaining(request, orderitem_id):
    """Given an orderitem_id, this returns a confirmation form."""
    
    try:
        orderitem = OrderItem.objects.get(pk = orderitem_id)
    except OrderItem.DoesNotExist:
        return bad_or_missing(request, _("The orderitem you have requested doesn't exist, or you don't have access to it."))
        
    amount = orderitem.product.customproduct.full_price
        
    data = {
        'orderitem' : orderitem_id,
        'amount' : amount,
        }
    form = CustomChargeForm(data)
    ctx = RequestContext(request, {'form' : form})
    return render_to_response('admin/charge_remaining_confirm.html', ctx)
    
def charge_remaining_post(request):
    if not request.method == 'POST':
        return bad_or_missing(request, _("No form found in request."))
    
    data = request.POST.copy()
    
    form = CustomChargeForm(data)
    if form.is_valid():
        data = form.cleaned_data
        try:
            orderitem = OrderItem.objects.get(pk = data['orderitem'])
        except OrderItem.DoesNotExist:
            return bad_or_missing(request, _("The orderitem you have requested doesn't exist, or you don't have access to it."))
        
        price = data['amount']
        line_price = price*orderitem.quantity
        orderitem.unit_price = price
        orderitem.line_item_price = line_price
        orderitem.save()
        #print "Orderitem price now: %s" % orderitem.line_item_price
        
        order = orderitem.order
    
        if not order.shipping_cost:
            order.shipping_cost = Decimal("0.00")
    
        if data['shipping']:
            order.shipping_cost += data['shipping']
            
        order.recalculate_total()
        
        request.user.message_set.create(message='Charged for custom product and recalculated totals.')

        notes = data['notes']
        if not notes:
            notes = 'Updated total price'
            
        order.add_status(notes=notes)
        
        return HttpResponseRedirect('/admin/contact/order/%i' % order.id)
    else:
        ctx = RequestContext(request, {'form' : form})
        return render_to_response('admin/charge_remaining_confirm.html', ctx)

