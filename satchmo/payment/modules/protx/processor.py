"""Prot/X Payment Gateway.

To use this module, enable it in your shop configuration, usually at http:yourshop/settings/

To override the connection urls specified below in `PROTX_DEFAULT_URLS, add a dictionary in 
your settings.py file called "PROTX_URLS", mapping the keys below to the urls you need for 
your store.  You only need to override the specific urls that have changed, the processor
will fall back to the defaults for any not specified in your dictionary.
"""
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from satchmo.configuration import config_value
from satchmo.payment.common.utils import record_payment
from urllib import urlencode
import forms
import logging
import urllib2

log = logging.getLogger('protx.processor')

PROTOCOL = "2.22"

PROTX_DEFAULT_URLS = {
    'LIVE_CONNECTION' : 'https://ukvps.protx.com/vpsDirectAuth/PaymentGateway3D.asp',
    'LIVE_CALLBACK' : 'https://ukvps.protx.com/vpsDirectAuth/Callback3D.asp',
    'TEST_CONNECTION' : 'https://ukvpstest.protx.com/vpsDirectAuth/PaymentGateway3D.asp',
    'TEST_CALLBACK' : 'https://ukvpstest.protx.com/vpsDirectAuth/Callback3D.asp',
    'SIMULATOR_CONNECTION' : 'https://ukvpstest.protx.com/VSPSimulator/VSPDirectGateway.asp',
    'SIMULATOR_CALLBACK' : 'https://ukvpstest.protx.com/VSPSimulator/VSPDirectCallback.asp' 
}

class PaymentProcessor(object):
    form = forms.ProtxPayShipForm
    packet = {}
    response = {}
    
    def __init__(self, settings):
        self.settings = settings
        self.packet = {
            'VPSProtocol': PROTOCOL,
            'TxType': settings.CAPTURE.value,
            'Vendor': settings.VENDOR.value,
            'Currency': settings.CURRENCY_CODE.value,
            }

    def _url(key):
        urls = PROTX_DEFAULT_URLS
        if hasattr(settings, 'PROTX_URLS'):
            urls.update(settings.PROTX_URLS)

        if self.settings.SIMULATOR.value:
            key = "SIMULATOR_" + key
        else:
            if self.settings.LIVE.value:
                key = "LIVE_" + key
            else:
                key = "TEST_" + key
        return urls[key]

    def _connection(self):
        return self._url('CONNECTION')
        
    connection = property(fget=_connection)
        
    def _callback(self):
        return self._url('CALLBACK')

    callback = property(fget=_callback)

    def prepareData(self, data):
        try:
            self.packet['VendorTxCode'] = data.id
            self.packet['Amount'] = data.total
            self.packet['Description'] = 'Online purchase'
            self.packet['CardType'] = data.CC.credit_type
            self.packet['card_holder'] = data.CC.card_holder
            self.packet['CardNumber'] = data.CC.decryptedCC
            self.packet['ExpiryDate'] = '%02d%s' % (data.CC.expire_month, str(data.CC.expire_year)[2:])
            if data.CC.start_month is not None:
                self.packet['StartDate'] = '%02d%s' % (data.CC.start_month, str(data.CC.start_year)[2:])
            if data.CC.ccv != '':
                self.packet['CV2'] = data.CC.ccv
            if data.CC.issue_num != '':
                self.packet['IssueNumber'] = data.CC.issue_num #'%02d' % int(data.CC.issue_num)
            addr = [data.billStreet1, data.billStreet2, data.billCity, data.billState]
            self.packet['BillingAddress'] = ', '.join(addr)
            self.packet['BillingPostCode'] = data.billPostalCode
        except Exception, e:
            log.error('preparing data, got error: %s', e)
            return
        self.postString = urlencode(self.packet)
        self.url = self.connection
        self.order = data
    
    def prepareData3d(self, md, pares):
        self.packet = {}
        self.packet['MD'] = md
        self.packet['PARes'] = pares
        self.postString = urlencode(self.packet)
        self.url = self.callback
        
    def process(self):
        # Execute the post to protx VSP DIRECT
        # print self.postString
        conn = urllib2.Request(url=self.url, data=self.postString)
        f = urllib2.urlopen(conn)
        result = f.read()
        log.debug('Process: url=%s\nPacket=%s\nResult=%s', self.url, self.packet, result)
        try:
            self.response = dict([ row.split('=', 1) for row in result.splitlines() ])
            status = self.response['Status']
            success = (status == 'OK')
            detail = self.response['StatusDetail']
            if success:
                record_payment(self.order, self.settings, amount=self.order.balance) #, transaction_id=transaction_id)
                return (True, status, detail)
            else:
                return (False, status, detail)
        except Exception, e:
            log.info('Error submitting payment: %s', e)
            return (False, 'ERROR', 'Invalid response from payment gateway')
        
