import os
import trml2pdf
from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader, Context
from django.shortcuts import get_object_or_404
from django.utils.encoding import smart_str
from django.views.decorators.cache import never_cache
from satchmo.contact.models import Order
from satchmo.shop.models import Config

def displayDoc(request, id, doc):
    # Create the HttpResponse object with the appropriate PDF headers for an invoice or a packing slip
    order = get_object_or_404(Order, pk=id)

    if doc == "invoice":
        filename = "mystore-invoice.pdf"
        template = "invoice.rml"
    elif doc == "packingslip":
        filename = "mystore-packingslip.pdf"
        template = "packing-slip.rml"
    elif doc == "shippinglabel":
        filename = "mystore-shippinglabel.pdf"
        template = "shipping-label.rml"
    else:
        return HttpResponseRedirect('/admin')
    response = HttpResponse(mimetype='application/pdf')
    response['Content-Disposition'] = 'attachment; filename=%s' % filename
    shopDetails = Config.get_shop_config()
    t = loader.get_template('pdf/%s' % template)
    templatedir = os.path.normpath(settings.TEMPLATE_DIRS[0])
    c = Context({
                'filename' : filename,
                'templateDir' : templatedir,
                'shopDetails' : shopDetails,
                'order' : order
                })
    pdf = trml2pdf.parseString(smart_str(t.render(c)))
    response.write(pdf)
    return response
displayDoc = staff_member_required(never_cache(displayDoc))

#Note - rendering an image in the file causes problems when running the dev
#server on windows.  Seems to be an issue with trml2pdf
