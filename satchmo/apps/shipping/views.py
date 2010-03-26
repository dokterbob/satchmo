import os
import urllib
from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader, Context
from django.shortcuts import get_object_or_404
from django.utils.encoding import smart_str
from django.views.decorators.cache import never_cache
from satchmo_store.shop.models import Order
from satchmo_store.shop.models import Config
from livesettings import config_value

def displayDoc(request, id, doc):
    import trml2pdf
    # Create the HttpResponse object with the appropriate PDF headers for an invoice or a packing slip
    order = get_object_or_404(Order, pk=id)
    shopDetails = Config.objects.get_current()
    filename_prefix = shopDetails.site.domain
    if doc == "invoice":
        filename = "%s-invoice.pdf" % filename_prefix
        template = "invoice.rml"
    elif doc == "packingslip":
        filename = "%s-packingslip.pdf" % filename_prefix
        template = "packing-slip.rml"
    elif doc == "shippinglabel":
        filename = "%s-shippinglabel.pdf" % filename_prefix
        template = "shipping-label.rml"
    else:
        return HttpResponseRedirect('/admin')
    response = HttpResponse(mimetype='application/pdf')
    response['Content-Disposition'] = 'attachment; filename=%s' % filename
    icon_uri = config_value('SHOP', 'LOGO_URI')
    t = loader.get_template(os.path.join('shop/pdf', template))
    c = Context({
                'filename' : filename,
                'iconURI' : icon_uri,
                'shopDetails' : shopDetails,
                'order' : order,
                })
    pdf = trml2pdf.parseString(smart_str(t.render(c)))
    response.write(pdf)
    return response
displayDoc = staff_member_required(never_cache(displayDoc))

