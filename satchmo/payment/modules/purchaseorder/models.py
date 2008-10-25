from django.db import models
from django.utils.translation import ugettext_lazy as _
from satchmo.shop.models import Order

class PurchaseOrder(models.Model):
    po_number = models.CharField(_('Customer PO Number'), max_length=20)
    order = models.ForeignKey(Order)
    
    def __unicode__(self):
        return "PO: #%s" % self.po_number
            

import config