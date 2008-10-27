from django.db import models
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext, ugettext_lazy as _
from satchmo.l10n.utils import moneyfmt
from satchmo.shop.models import Order

class PurchaseOrder(models.Model):
    po_number = models.CharField(_('Customer PO Number'), max_length=20)
    order = models.ForeignKey(Order)
    
    def __unicode__(self):
        return "PO: #%s" % self.po_number

    def order_link(self):
        return mark_safe(u'<a href="/admin/shop/order/%i/">%s #%i (%s)</a>' % (
            self.order.id,
            ugettext('Order'), 
            self.order.id, 
            moneyfmt(self.order.total)))
             
    order_link.allow_tags = True
    
            

import config