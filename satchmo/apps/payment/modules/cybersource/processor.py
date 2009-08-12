from django.template import Context, loader
from payment.modules.base import BasePaymentProcessor, ProcessorResult, NOTSET
from satchmo_utils.numbers import trunc_decimal
from django.utils.translation import ugettext_lazy as _

import urllib2
try:
    from xml.etree.ElementTree import fromstring
except ImportError:
    from elementtree.ElementTree import fromstring

# Response codes available at:
# http://apps.cybersource.com/library/documentation/sbc/api_guide/SB_API.pdf
CYBERSOURCE_RESPONSES = {
    '100' : 'Successful transaction.',
    '101' : 'The request is missing one or more required fields.',
    '102' : 'One or more fields in the request contains invalid data.',
    '104' : 'The merchantReferenceCode sent with this authorization request matches the merchantReferenceCode of another authorization request that you sent in the last 15 minutes.',
    '150' : 'Error: General system failure. ',
    '151' : 'Error: The request was received but there was a server timeout. This error does not include timeouts between the client and the server.',
    '152' : 'Error: The request was received, but a service did not finish running in time.',
    '201' : 'The issuing bank has questions about the request. You do not receive an authorization code in the reply message, but you might receive one verbally by calling the processor.',
    '202' : 'Expired card. You might also receive this if the expiration date you provided does not match the date the issuing bank has on file.',
    '203' : 'General decline of the card. No other information provided by the issuing bank.',
    '204' : 'Insufficient funds in the account.',
    '205' : 'Stolen or lost card.',
    '207' : 'Issuing bank unavailable.',
    '208' : 'Inactive card or card not authorized for card-not-present transactions.',
    '210' : 'The card has reached the credit limit. ',
    '211' : 'Invalid card verification number.',
    '221' : 'The customer matched an entry on the processor\'s negative file.',
    '231' : 'Invalid account number.',
    '232' : 'The card type is not accepted by the payment processor.',
    '233' : 'General decline by the processor.',
    '234' : 'There is a problem with your CyberSource merchant configuration.',
    '235' : 'The requested amount exceeds the originally authorized amount. Occurs, for example, if you try to capture an amount larger than the original authorization amount. This reason code only applies if you are processing a capture through the API.',
    '236' : 'Processor Failure',
    '238' : 'The authorization has already been captured. This reason code only applies if you are processing a capture through the API.',
    '239' : 'The requested transaction amount must match the previous transaction amount. This reason code only applies if you are processing a capture or credit through the API.',
    '240' : 'The card type sent is invalid or does not correlate with the credit card number.',
    '241' : 'The request ID is invalid. This reason code only applies when you are processing a capture or credit through the API.',
    '242' : 'You requested a capture through the API, but there is no corresponding, unused authorization record. Occurs if there was not a previously successful authorization request or if the previously successful authorization has already been used by another capture request. This reason code only applies when you are processing a capture through the API.',
    '243' : 'The transaction has already been settled or reversed.',
    '246' : 'The capture or credit is not voidable because the capture or credit information has already been submitted to your processor. Or, you requested a void for a type of transaction that cannot be voided. This reason code applies only if you are processing a void through the API.',
    '247' : 'You requested a credit for a capture that was previously voided. This reason code applies only if you are processing a void through the API.',
    '250' : 'Error: The request was received, but there was a timeout at the payment processor.',
    '520' : 'The authorization request was approved by the issuing bank but declined by CyberSource based on your Smart Authorization settings.',
}


class PaymentProcessor(BasePaymentProcessor):
    """
    Cybersource payment processing module
    You must have an account with Cybersource in order to use this module
    
    """
    def __init__(self, settings):
        super(PaymentProcessor, self).__init__('cybersource', settings)
        self.contents = ''
        if settings.LIVE.value:
            self.testflag = 'FALSE'
            self.connection = settings.CONNECTION.value
        else:
            self.testflag = 'TRUE'
            self.connection = settings.CONNECTION_TEST.value
            
        self.configuration = {
            'merchantID' : settings.MERCHANT_ID.value,
            'password' : settings.TRANKEY.value,
            }

    def prepare_content(self, order, amount):
        self.bill_to = {
            'firstName' : order.contact.first_name,
            'lastName' : order.contact.last_name,
            'street1': order.full_bill_street,
            'city': order.bill_city,
            'state' : order.bill_state,
            'postalCode' : order.bill_postal_code,
            'country': order.bill_country,
            'email' : order.contact.email,
            'phoneNumber' : order.contact.primary_phone,
            # Can add additional info here if you want to but it's not required
            }
        exp = order.credit_card.expirationDate.split('/')
        self.card = {
            'accountNumber' : order.credit_card.decryptedCC,
            'expirationMonth' : exp[0],
            'expirationYear' : exp[1],
            'cvNumber' : order.credit_card.ccv
            }
        currency = self.settings.CURRENCY_CODE.value
        currency = currency.replace("_", "")
        self.purchase_totals = {
            'currency' : currency,
            'grandTotalAmount' : trunc_decimal(amount, 2),
        }

    def capture_payment(self, testing=False, order=None, amount=NOTSET):
        """
        Creates and sends XML representation of transaction to Cybersource
        """
        if not order:
            order = self.order
            
        if order.paid_in_full:
            self.log_extra('%s is paid in full, no capture attempted.', order)
            self.record_payment()
            return ProcessorResult(self.key, True, _("No charge needed, paid in full."))

        self.log_extra('Capturing payment for %s', order)

        if amount==NOTSET:
            amount = order.balance

        self.prepare_content(order, amount)
        
        invoice = "%s" % order.id
        failct = order.paymentfailures.count()
        if failct > 0:
            invoice = "%s_%i" % (invoice, failct)
        
        # XML format is very simple, using ElementTree for generation would be overkill
        t = loader.get_template('shop/checkout/cybersource/request.xml')
        c = Context({
            'config' : self.configuration,
            'merchantReferenceCode' : invoice,
            'billTo' : self.bill_to,
            'purchaseTotals' : self.purchase_totals,
            'card' : self.card,
        })
        request = t.render(c)
        conn = urllib2.Request(url=self.connection, data=request)
        try:
            f = urllib2.urlopen(conn)
        except urllib2.HTTPError, e:
            # we probably didn't authenticate properly
            # make sure the 'v' in your account number is lowercase
            return ProcessorResult(self.key, False, 'Problem parsing results')

        f = urllib2.urlopen(conn)
        all_results = f.read()
        tree = fromstring(all_results)
        parsed_results = tree.getiterator('{urn:schemas-cybersource-com:transaction-data-1.26}reasonCode')
        try:
            reason_code = parsed_results[0].text
        except KeyError:
            return ProcessorResult(self.key, False, 'Problem parsing results')

        response_text = CYBERSOURCE_RESPONSES.get(reason_code, 'Unknown Failure')

        if reason_code == '100':
            payment = self.record_payment(order=order, amount=amount, 
                transaction_id="", reason_code=reason_code)
            return ProcessorResult(self.key, True, response_text, payment=payment)
        else:
            payment = self.record_failure(order=order, amount=amount, 
                transaction_id="", reason_code=reason_code, 
                details=response_text)
            
            return ProcessorResult(self.key, False, response_text)

if __name__ == "__main__":
    """
    For testing purposes only.
    Allows this module to be run as a script to test the connection
    
    """

    import os
    from livesettings import config_get_group

    # Set up some dummy classes to mimic classes being passed through Satchmo
    class testContact(object):
        pass
    class testCC(object):
        pass
    class testOrder(object):
        def __init__(self):
            self.contact = testContact()
            self.credit_card = testCC()
        def order_success(self):
            pass

    if not os.environ.has_key("DJANGO_SETTINGS_MODULE"):
        os.environ["DJANGO_SETTINGS_MODULE"]="satchmo_store.settings"

    settings_module = os.environ['DJANGO_SETTINGS_MODULE']
    settingsl = settings_module.split('.')
    settings = __import__(settings_module, {}, {}, settingsl[-1])

    sampleOrder = testOrder()
    sampleOrder.id = '1234'
    sampleOrder.contact.first_name = 'Chris'
    sampleOrder.contact.last_name = 'Smith'
    sampleOrder.contact.primary_phone = '801-555-9242'
    sampleOrder.contact.email = 'null@cybersource.com'
    sampleOrder.full_bill_street = '123 Main Street'
    sampleOrder.bill_postal_code = '12345'
    sampleOrder.bill_state = 'TN'
    sampleOrder.bill_city = 'Some City'
    sampleOrder.bill_country = 'US'
    sampleOrder.total = "27.00"
    sampleOrder.balance = "27.00"
    sampleOrder.credit_card.decryptedCC = '6011000000000012'
    sampleOrder.credit_card.expirationDate = "10/09"
    sampleOrder.credit_card.ccv = "144"

    cybersource_settings = config_get_group('PAYMENT_CYBERSOURCE')
    if cybersource_settings.LIVE.value:
        print "Warning.  You are submitting a live order.  CYBERSOURCE system is set LIVE."
        
    processor = PaymentProcessor(cybersource_settings)
    processor.prepare_data(sampleOrder)
    results = processor.process(testing=True)
    print results


