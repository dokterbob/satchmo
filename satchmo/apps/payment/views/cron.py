from datetime import datetime, timedelta
from decimal import Decimal
from django.http import HttpResponse
from django.utils.translation import ugettext, ugettext_lazy as _
from livesettings import config_get_group, config_value
from satchmo_store.shop.models import Order, OrderItem, OrderPayment
from satchmo_utils.views import bad_or_missing
import logging

log = logging.getLogger('payment.views.cron')

def cron_rebill(request=None):
    """Rebill customers with expiring recurring subscription products
    This can either be run via a url with GET key authentication or
    directly from a shell script.
    """
    #TODO: support re-try billing for failed transactions

    if request is not None:
        if not config_value('PAYMENT', 'ALLOW_URL_REBILL'):
            return bad_or_missing(request, _("Feature is not enabled."))
        if 'key' not in request.GET or request.GET['key'] != config_value('PAYMENT','CRON_KEY'):
            return HttpResponse("Authentication Key Required")

    expiring_subscriptions = OrderItem.objects.filter(expire_date__gte=datetime.now()).order_by('order', 'id', 'expire_date')
    for item in expiring_subscriptions:
        if item.product.is_subscription:#TODO - need to add support for products with trial but non-recurring
            if item.product.subscriptionproduct.recurring_times and item.product.subscriptionproduct.recurring_times + item.product.subscriptionproduct.get_trial_terms().count() == OrderItem.objects.filter(order=item.order, product=item.product).count():
                continue
            if item.expire_date == datetime.date(datetime.now()) and item.completed:
                if item.id == OrderItem.objects.filter(product=item.product, order=item.order).order_by('-id')[0].id:
                    #bill => add orderitem, recalculate total, porocess card
                    new_order_item = OrderItem(order=item.order, product=item.product, quantity=item.quantity, unit_price=item.unit_price, line_item_price=item.line_item_price)
                    #if product is recurring, set subscription end
                    if item.product.subscriptionproduct.recurring:
                        new_order_item.expire_date = item.product.subscriptionproduct.calc_expire_date()
                    #check if product has 2 or more trial periods and if the last one paid was a trial or a regular payment.
                    ordercount = item.order.orderitem_set.all().count()
                    if item.product.subscriptionproduct.get_trial_terms().count() > 1 and item.unit_price == item.product.subscriptionproduct.get_trial_terms(ordercount - 1).price:
                        new_order_item.unit_price = item.product.subscriptionproduct.get_trial.terms(ordercount).price
                        new_order_item.line_item_price = new_order_item.quantity * new_order_item.unit_price
                        new_order_item.expire_date = item.product.subscriptionproduct.get_trial_terms(ordercount).calc_expire_date()
                    new_order_item.save()
                    item.order.recalculate_total()
#                    if new_order_item.product.subscriptionproduct.is_shippable == 3:
#                        item.order.total = item.order.total - item.order.shipping_cost
#                        item.order.save()
                    payments = item.order.payments.all()[0]
                    #list of ipn based payment modules.  Include processors that use 3rd party recurring billing.
                    ipn_based = ['PAYPAL']
                    if not payments.payment in ipn_based and item.order.balance > 0:
                        #run card
                        #Do the credit card processing here & if successful, execute the success_handler
                        from livesettings import config_get_group
                        payment_module = config_get_group('PAYMENT_%s' % payments.payment)
                        credit_processor = payment_module.MODULE.load_module('processor')
                        processor = credit_processor.PaymentProcessor(payment_module)
                        processor.prepare_data(item.order)
                        result = processor.process()
        
                        if result.payment:
                            reason_code = result.payment.reason_code
                        else:
                            reason_code = "unknown"
                        log.info("""Processing %s recurring transaction with %s
                            Order #%i
                            Results=%s
                            Response=%s
                            Reason=%s""",
                            payment_module.LABEL.value,
                            payment_module.KEY.value,
                            item.order.id,
                            result.success,
                            reason_code,
                            result.message)

                        if result.success:
                            #success handler
                            item.order.add_status(status='New', notes = ugettext("Subscription Renewal Order successfully submitted"))
                            new_order_item.completed = True
                            new_order_item.save()
                            orderpayment = OrderPayment(order=item.order, amount=item.order.balance, payment=unicode(payment_module.KEY.value))
                            orderpayment.save()
    return HttpResponse()
