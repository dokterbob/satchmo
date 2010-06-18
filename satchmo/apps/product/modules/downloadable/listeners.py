from django.conf.urls.defaults import patterns as patterns_func
from django.utils.translation import ugettext
import product
from product import signals as product_signals
from product.modules.downloadable.models import DownloadLink
from satchmo_store.contact import signals as contact_signals
from satchmo_store.shop import notification
from satchmo_store.shop import signals
from satchmo_store.shop.listeners import recalc_total_on_contact_change, decrease_inventory_on_sale

from signals_ahoy.signals import collect_urls

import logging

log = logging.getLogger('product.modules.downloadable.listeners')

def add_download_urls(sender=None, patterns=None, section=None, **kwargs):
    # override top-level one, so that we don't get the PRODUCT_SLUG prefix for
    # backward-compatibility.
    if not section == '__init__':
        return

    urlpatterns = patterns_func('product.modules.downloadable.views',
        (r'^download/process/(?P<download_key>\w+)/$', 'process', {}, 'satchmo_download_process'),
        (r'^download/send/(?P<download_key>\w+)/$', 'send_file', {}, 'satchmo_download_send'),
    )

    if patterns:
        patterns += urlpatterns

def create_download_link(product=None, order=None, subtype=None, **kwargs):
    """Creates a download link for a Downloadable Product on order success."""
    if product and order and subtype == "download":
        new_link = DownloadLink(downloadable_product=product, order=order,
            key=product.create_key(), num_attempts=0)
        new_link.save()
    else:
        log.debug("ignoring subtype_order_success signal, looking for download product, got %s", subtype)


def ship_downloadable_order(order=None, **kwargs):
    if order.is_downloadable and not order.status == 'Shipped':
        order.add_status('Shipped', ugettext("Order immediately available for download"))

    product_signals.subtype_order_success.connect(create_download_link, sender=None)
    contact_signals.satchmo_contact_location_changed.connect(recalc_total_on_contact_change, sender=None)
    signals.order_success.connect(decrease_inventory_on_sale)
    signals.order_success.connect(notification.order_success_listener, sender=None)
    signals.order_success.connect(ship_downloadable_order, sender=None)

def start_default_listening():
    """Add required default listeners"""
    collect_urls.connect(add_download_urls, sender=product)
    product_signals.subtype_order_success.connect(create_download_link, sender=None)
    signals.order_success.connect(ship_downloadable_order, sender=None)

    log.debug('Added downnloadable product listeners')
