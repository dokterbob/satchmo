"""
This module requires that the tcclink library and the associated python bindings are installed.
You can get it from your TrustCommerce account d/l links or from -
http://www.trustcommerce.com/tclink.html
"""

from django.utils.translation import ugettext_lazy as _
from satchmo.payment.common.utils import record_payment
import tclink

class PaymentProcessor(object):
    # TrustCommerce payment processing module
    # You must have an account (or a test/trial account) in order to use this module
    # note that although this can be done using a url post like AuthorizeNet, 
    # the tclink method shown here is extremely simple, and more secure, and uses
    # backp servers guaranteeing uptime versus the singe-server https method -  
    # see TC for details.
    
    def __init__(self, settings):
        self.demo = 'y'
        self.AVS = 'n'
        self.settings = settings 
        self.custid = settings.LOGIN.value
        self.password = settings.PASSWORD.value
        if settings.LIVE.value:
            self.demo = 'n'
        if settings.AVS.value:
            self.AVS = 'y'
        self.auth = settings.AUTH_TYPE.value
        self.tclink_version = tclink.getVersion()

    def prepareData(self, data):
        self.order = data
        # See tclink developer's guide for additional fields and info
        # convert amount to cents, no decimal point
        amount = str(data.balance).replace ('.', '')

        # convert exp date to mmyy from mm/yy or mm/yyyy
        exp = '%.2d%.2d' % tuple (int (mmyy) % 100 for mmyy in data.credit_card.expirationDate.split ('/'))

        self.transactionData = {
            # account data
            'custid'	: self.custid,
            'password'	: self.password,
            'demo'	: self.demo,

            # Customer data
            'name'  	: data.contact.first_name + ' ' + data.contact.last_name,
            'address1'	: data.full_bill_street,
            'city'	: data.bill_city,
            'state' 	: data.bill_state,
            'zip' 	: str(data.bill_postal_code),
            'country'	: data.bill_country,
            'phone' 	: str(data.contact.primary_phone.phone),
            # other possibiliities include email, ip, offlineauthcode, etc 

            # transaction data
            'media'     : 'cc',
            'action'	: self.auth,  	# or 'sale', 'credit', etc - see tclink dev guide
            'amount' 	: amount,	# in cents
            'cc'	: data.credit_card.decryptedCC,  # use '4111111111111111' for test
            'exp'	: exp, 		# 4 digits eg 0108
            'cvv'	: str(data.credit_card.ccv),
            'avs'	: self.AVS,		# address verification - see tclink dev guide
            'ticket'	: 'Order: ' + str(data.credit_card.orderpayment_id),
            'operator'	: 'Satchmo'
            }
        
    def process(self):
        # process thre transaction through tclink
        result = tclink.send (self.transactionData)
        status = result ['status']
        if status == 'approved':
            record_payment(self.order, self.settings, amount=self.order.balance)
            return (True, status, result)
        if status == 'decline':
            msg = _(u'Transaction was declined.  Reason: %s' % result['declinetype'])
            return (False, status, msg)
        if status == 'baddata':
            msg = _(u'Improperly formatted data. Offending fields: %s' % result['offenders'])
            return (False, status, msg)
        else:
            msg = _(u'An error occurred: %s' % result['errortype'])
            return (False, status, msg)
  
        
if __name__ == "__main__":
    #####
    # This is for testing - enabling you to run from the command line & make sure everything is ok
    #####
    import os
    from satchmo.configuration import config_get_group 
    
    # Set up some dummy classes to mimic classes being passed through Satchmo
    class testContact(object):
        pass
    class testCC(object):
        pass
    class testOrder(object):
        def __init__(self):
            self.contact = testContact()
            self.CC = testCC()
        def order_sucess(self):
            pass


    if not os.environ.has_key("DJANGO_SETTINGS_MODULE"):
        os.environ["DJANGO_SETTINGS_MODULE"]="satchmo.settings"
   
    sampleOrder = testOrder()
    sampleOrder.contact.first_name = 'Chris'
    sampleOrder.contact.last_name = 'Smith'
    sampleOrder.contact.primary_phone = '801-555-9242'
    sampleOrder.fullBillStreet = '123 Main Street'
    sampleOrder.billPostalCode = '12345'
    sampleOrder.billState = 'TN'
    sampleOrder.billCity = 'Some City'
    sampleOrder.billCountry = 'US'
    sampleOrder.balance = "27.00"
    sampleOrder.total = "27.00"
    sampleOrder.CC.decryptedCC = '4111111111111111'
    sampleOrder.CC.expirationDate = "10/09"
    sampleOrder.CC.ccv = "123"
    sampleOrder.CC.order = "987654"
    
    trustcommerce_settings = config_get_group('PAYMENT_TRUSTCOMMERCE')

    processor = PaymentProcessor (trustcommerce_settings)
    processor.prepareData (sampleOrder)
    results, reason_code, msg = processor.process()
    print results, "::", msg

