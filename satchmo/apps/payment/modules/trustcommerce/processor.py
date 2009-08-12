"""
This module requires that the tcclink library and the associated python bindings are installed.
You can get it from your TrustCommerce account d/l links or from -
http://www.trustcommerce.com/tclink.html
"""

from django.utils.translation import ugettext_lazy as _
from payment.modules.base import BasePaymentProcessor, ProcessorResult, NOTSET
import tclink

class PaymentProcessor(BasePaymentProcessor):
    # TrustCommerce payment processing module
    # You must have an account (or a test/trial account) in order to use this module
    # note that although this can be done using a url post like AuthorizeNet, 
    # the tclink method shown here is extremely simple, and more secure, and uses
    # backp servers guaranteeing uptime versus the singe-server https method -  
    # see TC for details.
    
    def __init__(self, settings):
        super(PaymentProcessor, self).__init__('trustcommerce', settings)
        self.demo = 'y'
        self.AVS = 'n'
        self.custid = settings.LOGIN.value
        self.password = settings.PASSWORD.value
        if settings.LIVE.value:
            self.demo = 'n'
        if settings.AVS.value:
            self.AVS = 'y'
        self.auth = settings.AUTH_TYPE.value
        self.tclink_version = tclink.getVersion()

    def prepare_post(self, data, amount):
        # See tclink developer's guide for additional fields and info
        # convert amount to cents, no decimal point
        amount = unicode((amount * 100).to_integral()) 

        # convert exp date to mmyy from mm/yy or mm/yyyy
        cc = data.credit_card 
        exp = u"%.2d%.2d" % (int(cc.expire_month), (int(cc.expire_year) % 100)) 

        invoice = "%s" % data.id
        failct = data.paymentfailures.count()
        if failct > 0:
            invoice = "%s_%i" % (invoice, failct)

        self.transactionData = {
            # account data
            'custid'	: self.custid,
            'password'	: self.password,
            'demo'	: self.demo,

            # Customer data
            'name'  	: data.contact.first_name + u' ' + data.contact.last_name,
            'address1'	: data.full_bill_street,
            'city'	: data.bill_city,
            'state' 	: data.bill_state,
            'zip' 	:data.bill_postal_code,
            'country'	: data.bill_country,
            'phone' 	: data.contact.primary_phone.phone,
            # other possibiliities include email, ip, offlineauthcode, etc 

            # transaction data
            'media'     : 'cc',
            'action'	: self.auth,  	# or 'sale', 'credit', etc - see tclink dev guide
            'amount' 	: amount,	# in cents
            'cc'	: cc.decryptedCC,  # use '4111111111111111' for test
            'exp'	: exp, 		# 4 digits eg 0108
            'cvv'	: cc.ccv,
            'avs'	: self.AVS,		# address verification - see tclink dev guide
            'ticket'	: u'Order: %s ' % invoice,
            'operator'	: 'Satchmo'
            }
        for key, value in self.transactionData.items(): 
            if isinstance(value, unicode): 
                self.transactionData[key] = value.encode('utf7',"ignore") 
        
    def capture_payment(self, testing=False, order=None, amount=NOTSET):
        """process the transaction through tclink"""
        if not order:
            order = self.order

        if amount == NOTSET:
            amount = order.balance
            
        if order.paid_in_full:
            self.log_extra('%s is paid in full, no capture attempted.', order)
            self.record_payment()
            return ProcessorResult(self.key, True, _("No charge needed, paid in full."))

        self.log_extra('Capturing payment for %s', order)

        self.prepare_post(order, amount)

        result = tclink.send(self.transactionData)
        status = result ['status']
        payment = None
        success = False
        
        if status == 'approved':
            payment = self.record_payment(order=order, amount=amount, 
                transaction_id="", reason_code=status)
            success = True
            msg = unicode(result)

        else:
            if status == 'decline':
                msg = _(u'Transaction was declined.  Reason: %s' % result['declinetype'])
                failmsg = u'Transaction was declined.  Reason: %s' % result['declinetype']

            elif status == 'baddata':
                msg = _(u'Improperly formatted data. Offending fields: %s' % result['offenders'])
                failmsg = u'Improperly formatted data. Offending fields: %s' % result['offenders']

            else:
                status = "error"
                msg = _(u'An error occurred: %s' % result['errortype'])
                failmsg = u'An error occurred: %s' % result['errortype']

            payment = self.record_failure(order=order, amount=amount, 
                transaction_id="", reason_code=status, 
                details=failmsg)

        return ProcessorResult(self.key, success, msg, payment=payment)
        
if __name__ == "__main__":
    #####
    # This is for testing - enabling you to run from the command line & make sure everything is ok
    #####
    import os
    from livesettings import config_get_group 
    from decimal import Decimal
    
    # Set up some dummy classes to mimic classes being passed through Satchmo
    class testContact(object):
        pass
    class testCC(object):
        pass
    class phone(object):
        pass
    class testOrder(object):
        def __init__(self):
            self.contact = testContact()
            self.credit_card = testCC()
            self.contact.primary_phone = phone()
        def order_sucess(self):
            pass


    if not os.environ.has_key("DJANGO_SETTINGS_MODULE"):
        os.environ["DJANGO_SETTINGS_MODULE"]="satchmo_store.settings"
   
    sampleOrder = testOrder()
    sampleOrder.contact.first_name = 'Chris'
    sampleOrder.contact.last_name = 'Smith'
    sampleOrder.contact.primary_phone.phone = '801-555-9242'
    sampleOrder.full_bill_street = '123 Main Street'
    sampleOrder.bill_postal_code = '12345'
    sampleOrder.bill_state = 'TN'
    sampleOrder.bill_city = 'Some City'
    sampleOrder.bill_country = 'US'
    sampleOrder.balance = Decimal("27.00")
    sampleOrder.total = Decimal("27.00")
    sampleOrder.credit_card.decryptedCC = '4111111111111111'
    sampleOrder.credit_card.expire_month = "10"
    sampleOrder.credit_card.expire_year = "2010"
    sampleOrder.credit_card.ccv = "123"
    sampleOrder.credit_card.order = "987654"
    sampleOrder.credit_card.orderpayment_id = "123"
    
    trustcommerce_settings = config_get_group('PAYMENT_TRUSTCOMMERCE')

    processor = PaymentProcessor (trustcommerce_settings)
    processor.prepare_data(sampleOrder)
    results = processor.process()
    print results

