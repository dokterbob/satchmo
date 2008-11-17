from satchmo.configuration import config_get_group
import logging

class BasePaymentProcessor(object):
    
    def __init__(self, label, payment_module):
        self.settings = payment_module
        self.label = label
        self.log = logging.getLogger('payment.' + label)
        self.order = None
                
    def allowed(self, user, amount):
        """Allows different payment processors to be allowed for certain situations."""
        return True
        
    def can_process(self):
        return True
        
    def can_refund(self):
        return False
        
    def can_recur_bill(self):
        return True
    
    def get_recurring_orderitems(self):
        """Iterate through the order and get all recurring billing items"""
        subscriptions = []
        for orderitem in self.order.orderitem_set.all():
            product = orderitem.product
            if product.is_subscription:
                self.log_extra('Found subscription product: %s', product.slug)
                if product.subscriptionproduct.recurring:
                    self.log_extra('Subscription is recurring: %s', product.slug)
                    subscriptions.append(orderitem)
                elif product.subscriptionproduct.trial_set.count() > 0:
                    self.log_extra('Not recurring, but it has a trial: %s', product.slug)
                    subscriptions.append(orderitem)
                else:
                    self.log_extra('Not a recurring product: %s ', product.slug)
            else:
                self.log_extra('Not a subscription product: %s', product.slug)
        return subscriptions
    
    def is_live(self):
        return self.settings.LIVE.value
    
    def log_extra(self, msg, *args):
        """Send a log message if EXTRA_LOGGING is set in settings."""
        if self.settings.EXTRA_LOGGING.value:
            self.log.info("(Extra logging) " + msg, *args)

    def prepareData(self, order):
        self.order = order

    def process(self):
        """Override me.  This will process the payment."""
        #return ProcessorResult(True, _('OK'))
        return (True, _('OK'))
        
# class ProcessorResult(object):
#     
#     def __init__(self, success, message):
#         self.success = success
#         self.message = message
