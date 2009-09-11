from django.utils.translation import ugettext_lazy as _
from satchmo_store import get_version
from satchmo_store.contact.models import Contact
from satchmo_store.shop.models import Order, Cart
from satchmo_store.shop.signals import satchmo_context
from threaded_multihost import threadlocals
import datetime
import logging
import operator
from product.models import Product, ProductVariation


log = logging.getLogger('satchmo_toolbar')

def add_toolbar_context(sender, context={}, **kwargs):
    user = threadlocals.get_current_user()
    if user and user.is_staff:
        request_path = context['request'].META['PATH_INFO']
        slug = request_path.split('/')[-2]
        total_sales = 0
        show_sales = False
        variation_items = []
        try:
            product = Product.objects.get(slug=slug)
            show_sales = True
            subtypes = product.get_subtypes()
            if 'ConfigurableProduct' in subtypes:
                total_sales = 0
                all_variations = ProductVariation.objects.filter(parent=product)
                for variation in all_variations:
                    total_sales += variation.product.total_sold
                    variation_items.append(variation.product)
            else:
                total_sales = product.total_sold
                
        except:
            pass
            
        st = {}
        st['st_satchmo_version'] = get_version()
        newq = Order.objects.filter(status__exact = 'New')
        st['st_new_order_ct'] = newq.count()
        amounts = newq.values_list('total', flat=True)
        if amounts:
            newtotal = reduce(operator.add, amounts)
        else:
            newtotal = 0
        st['st_new_order_total'] = newtotal
        st['st_total_sold'] = total_sales
        st['st_show_sales'] = show_sales
        st['st_variations'] = variation_items
        week = datetime.datetime.today()-datetime.timedelta(days=7)
        day = datetime.datetime.today()-datetime.timedelta(days=1)
        hours = datetime.datetime.today()-datetime.timedelta(hours=1)
        cartweekq = Cart.objects.filter(date_time_created__gte=week)
        cartdayq = Cart.objects.filter(date_time_created__gte=day)
        carthourq = Cart.objects.filter(date_time_created__gte=hours)
        st['st_cart_7d_ct'] = cartweekq.count()
        st['st_cart_1d_ct'] = cartdayq.count()
        st['st_cart_1h_ct'] = carthourq.count()
        
        st['st_contacts_ct'] = Contact.objects.all().count()
        st['st_contacts_7d_ct'] = Contact.objects.filter(create_date__gte=week).count()
        # edits = []
        # st['st_edits'] = edits        
        
        context.update(st)
        

def start_listening():
    log.debug('Satchmo toolbar ready')
    satchmo_context.connect(add_toolbar_context)
