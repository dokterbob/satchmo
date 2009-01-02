try:
    from decimal import Decimal
except:
    from django.utils._decimal import Decimal

from django.template import loader, Context
from django.utils.translation import ugettext_lazy as _
from payment.modules.base import BasePaymentProcessor
from payment.utils import record_payment
from satchmo_store.shop.models import Config
from tax.utils import get_tax_processor
from satchmo_utils import trunc_decimal
from urllib import urlencode
from xml.dom import minidom
import logging
import urllib2

class PaymentProcessor(BasePaymentProcessor):
    """
    Authorize.NET payment processing module
    You must have an account with authorize.net in order to use this module.
    
    Additionally, you must have ARB enabled in your account to use recurring billing.
    """
    def __init__(self, settings):
        super(PaymentProcessor, self).__init__('authorizenet', settings)
        self.arb_enabled = settings.ARB.value
                            
    def getRecurringChargeData(self, testing=False):
        """Build the list of dictionaries needed to process a recurring charge.
        
        Because Authorize can only take one subscription at a time, we build a list
        of the transaction dictionaries, for later sequential posting.
        """
        if not self.arb_enabled:
            return []
        
        # get all subscriptions from the order
        subscriptions = self.get_recurring_orderitems()
        
        if len(subscriptions) == 0:
            self.log_extra('No subscription items')
            return []

        settings = self.settings            
        # set up the base dictionary
        trans = {}

        if self.is_live():
            conn = settings.ARB_CONNECTION.value
            self.log_extra('Using live recurring charge connection.')
        else:
            conn = settings.ARB_CONNECTION_TEST.value
            self.log_extra('Using test recurring charge connection.')
        
        shop_config = Config.objects.get_current()
        
        trans['connection'] = conn
        trans['config'] = {
            'merchantID' : settings.LOGIN.value,
            'transactionKey' : settings.TRANKEY.value,
            'shop_name' : shop_config.store_name,
        }
        trans['order'] = self.order
        trans['card'] = self.order.credit_card
        trans['card_expiration'] =  "%4i-%02i" % (self.order.credit_card.expire_year, self.order.credit_card.expire_month)
        
        translist = []
        taxer = get_tax_processor(user = self.order.contact.user)
        
        for subscription in subscriptions:
            product = subscription.product
            subtrans = trans.copy()
            subtrans['subscription'] = subscription
            subtrans['product'] = product
            
            sub = product.subscriptionproduct
            
            trial = sub.get_trial_terms(0)
            if trial:
                price = trunc_decimal(trial.price, 2)
                trial_amount = price
                if price and subscription.product.taxable:
                    trial_amount = taxer.by_price(subscription.product.taxClass, price)
                    #todo, maybe add shipping for trial?
                amount = sub.recurring_price()
                trial_occurrences = trial.occurrences
                if not trial_occurrences:
                    self.log.warn("Trial expiration period is less than one recurring billing cycle. " +
                        "Authorize does not allow this, so the trial period has been adjusted to be equal to one recurring cycle.")
                    trial_occurrences = 1
            else:
                trial_occurrences = 0
                trial_amount = Decimal('0.00')
                amount = subscription.total_with_tax

            occurrences = sub.recurring_times + trial_occurrences
            if occurrences > 9999:
                occurrences = 9999

            subtrans['occurrences'] = occurrences
            subtrans['trial_occurrences'] = trial_occurrences
            subtrans['trial'] = trial
            subtrans['trial_amount'] = trunc_decimal(trial_amount, 2)
            subtrans['amount'] = trunc_decimal(amount, 2)
            if trial:
                charged_today = trial_amount
            else:
                charged_today = amount
            
            charged_today = trunc_decimal(charged_today, 2)
                
            subtrans['charged_today'] = charged_today
            translist.append(subtrans)
            
        return translist
        
    def getStandardChargeData(self):
        """Build the dictionary needed to process a credit card charge"""
        order = self.order
        if order.paid_in_full:
            self.log_extra('No standard charges, order is paid in full.')
            return None

        settings = self.settings
        trans = {}
        balance = trunc_decimal(order.balance, 2)
        trans['amount'] = balance
        
        if self.is_live():
            conn = settings.CONNECTION.value
            self.log_extra('Using live connection.')
        else:
            testflag = 'TRUE'
            conn = settings.CONNECTION_TEST.value
            self.log_extra('Using test connection.')
            
        if self.settings.SIMULATE.value:
            testflag = 'TRUE'
        else:
            testflag = 'FALSE'

        trans['connection'] = conn
            
        capture = settings.CAPTURE.value
        trans['authorize_only'] = not capture

        if capture:
            transaction_type = 'AUTH_CAPTURE'
            self.log_extra('Will capture payment.')
        else:
            transaction_type = 'AUTH_ONLY'
            self.log_extra('Authorizing payment, no capture.')
                        
        trans['configuration'] = {
            'x_login' : settings.LOGIN.value,
            'x_tran_key' : settings.TRANKEY.value,
            'x_version' : '3.1',
            'x_relay_response' : 'FALSE',
            'x_test_request' : testflag,
            'x_delim_data' : 'TRUE',
            'x_delim_char' : '|',
            'x_type': transaction_type,
            'x_method': 'CC',
            }
        
        self.log_extra('standard charges configuration: %s', trans['configuration'])
        
        trans['custBillData'] = {
            'x_first_name' : order.contact.first_name,
            'x_last_name' : order.contact.last_name,
            'x_address': order.full_bill_street,
            'x_city': order.bill_city,
            'x_state' : order.bill_state,
            'x_zip' : order.bill_postal_code,
            'x_country': order.bill_country,
            'x_phone' : order.contact.primary_phone.phone
            }
    
        self.log_extra('standard charges configuration: %s', trans['custBillData'])
        balance = trunc_decimal(order.balance, 2)
        trans['amount'] = balance
        
        trans['transactionData'] = {
            'x_amount' : balance,
            'x_card_num' : order.credit_card.decryptedCC,
            'x_exp_date' : order.credit_card.expirationDate,
            'x_card_code' : order.credit_card.ccv,
            'x_invoice_num' : order.id
            }

        part1 = urlencode(trans['configuration']) + "&"
        part2 = "&" + urlencode(trans['custBillData'])
        trans['postString'] = part1 + urlencode(trans['transactionData']) + part2
        
        redactedData = {
            'x_amount' : balance,
            'x_card_num' : order.credit_card.display_cc,
            'x_exp_date' : order.credit_card.expirationDate,
            'x_card_code' : "REDACTED",
            'x_invoice_num' : order.id
        }
        self.log_extra('standard charges transactionData: %s', redactedData)
        trans['logPostString'] = part1 + urlencode(redactedData) + part2
        
        return trans

    def process(self, testing=False):
        """Process payments."""
        
        self.log_extra('processing payment')
        recurlist = self.getRecurringChargeData()
        if recurlist:
            success, reason, response = self.process_recurring_subscriptions(recurlist, testing)
            if not success:
                self.log_extra('recur payment failed, aborting the rest of the module')
                return (success, reason, response)

        standard = self.getStandardChargeData()
        if standard:
            success, reason, response = self.process_standard(standard, testing)
            
        return success, reason, response
        
    def process_recurring_subscriptions(self, recurlist, testing=False):
        """Post all subscription requests."""    
        
        for recur in recurlist:
            success, reason, response, subscription_id = self.process_recurring_subscription(recur, testing=testing)
            if success:
                if not testing:
                    record_payment(self.order, self.settings, amount=recur['charged_today'], transaction_id=subscription_id)
            else:
                self.log.info("Failed to process recurring subscription, %s: %s", reason, response)
                break
        
        return success, reason, response
        
    def process_recurring_subscription(self, data, testing=False):
        """Post one subscription request."""
        self.log_extra('Processing subscription: %s', data['product'].slug)
        
        t = loader.get_template('shop/checkout/authorizenet/arb_create_subscription.xml')
        ctx = Context(data)
        request = t.render(ctx)
        
        if self.settings.EXTRA_LOGGING.value:
            data['redact'] = True
            ctx = Context(data)
            redacted = t.render(ctx)
            self.log_extra('Posting data to: %s\n%s', data['connection'], redacted)
        
        headers = {'Content-type':'text/xml'}
        conn = urllib2.Request(data['connection'], request, headers)
        try:
            f = urllib2.urlopen(conn)
            all_results = f.read()
        except urllib2.URLError, ue:
            self.log.error("error opening %s\n%s", data['connection'], ue)
            return (False, 'ERROR', _('Could not talk to Authorize.net gateway'))
        
        self.log_extra('Authorize response: %s', all_results)
        
        subscriptionID = None
        try:
            response = minidom.parseString(all_results)
            doc = response.documentElement
            reason = doc.getElementsByTagName('code')[0].firstChild.nodeValue
            response_text = doc.getElementsByTagName('text')[0].firstChild.nodeValue                
            result = doc.getElementsByTagName('resultCode')[0].firstChild.nodeValue
            success = result == "Ok"

            if success:
                #refID = doc.getElementsByTagName('refId')[0].firstChild.nodeValue
                subscriptionID = doc.getElementsByTagName('subscriptionId')[0].firstChild.nodeValue
        except Exception, e:
            self.log.error("Error %s\nCould not parse response: %s", e, all_results)
            success = False
            reason = "Parse Error"
            response_text = "Could not parse response"
            
        return success, reason, response_text, subscriptionID
        
    def process_standard(self, data, testing=False):
        """Execute the post to Authorize Net.
        
        Params:
        - data: dictionary as returned by getStandardChargeData
        - testing: if true, then don't record the payment
        
        Returns:
        - success: boolean
        - code: response code
        - detail: response detail
        """
        if data['authorize_only']:
            self.log.info("About to process standard payment [AUTHORIZE ONLY]: %(connection)s\n%(logPostString)s", data, )
        else:
            self.log.info("About to process standard payment [AUTH/CAPTURE]: %(connection)s\n%(logPostString)s", data)

        conn = urllib2.Request(url=data['connection'], data=data['postString'])
        try:
            f = urllib2.urlopen(conn)
            all_results = f.read()
            self.log_extra('Authorize response: %s', all_results)
        except urllib2.URLError, ue:
            self.log.error("error opening %s\n%s", data['connection'], ue)
            return (False, 'ERROR', _('Could not talk to Authorize.net gateway'))
            
        parsed_results = all_results.split(data['configuration']['x_delim_char'])
        response_code = parsed_results[0]
        reason_code = parsed_results[1]
        response_text = parsed_results[3]
        transaction_id = parsed_results[6]
        success = response_code == '1'
        
        if success and not testing:
            self.log_extra('Success, recording payment')
            record_payment(self.order, self.settings, amount=data['amount'], transaction_id=transaction_id)
                
        self.log_extra("Returning success=%s, reason=%s, response_text=%s", success, reason_code, response_text)
        return(success, reason_code, response_text)

if __name__ == "__main__":
    """
    This is for testing - enabling you to run from the command line and make
    sure everything is ok
    """
    import os
    from livesettings import config_get_group
    import config

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
    sampleOrder.contact.first_name = 'Chris'
    sampleOrder.contact.last_name = 'Smith'
    sampleOrder.contact.primary_phone = '801-555-9242'
    sampleOrder.full_bill_street = '123 Main Street'
    sampleOrder.bill_postal_code = '12345'
    sampleOrder.bill_state = 'TN'
    sampleOrder.bill_city = 'Some City'
    sampleOrder.bill_country = 'US'
    sampleOrder.total = "27.01"
    sampleOrder.balance = "27.01"
    sampleOrder.credit_card.decryptedCC = '6011000000000012'
    sampleOrder.credit_card.expirationDate = "10/11"
    sampleOrder.credit_card.ccv = "144"

    authorize_settings = config_get_group('PAYMENT_AUTHORIZENET')
    if authorize_settings.LIVE.value:
        print "Warning.  You are submitting a live order.  AUTHORIZE.NET system is set LIVE."
        
    processor = PaymentProcessor(authorize_settings)
    processor.prepareData(sampleOrder)
    results, reason_code, msg = processor.process(testing=True)
    print results,"::", msg


