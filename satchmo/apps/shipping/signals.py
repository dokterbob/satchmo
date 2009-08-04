import django.dispatch

shipping_data_query = django.dispatch.Signal()
# shipping_choices_query.send(sender=cart, cart=cart, 
#     paymentmodule=paymentmodule, contact=contact, 
#     default_view_tax=default_view_tax, order=order,
#     shipping_options = shipping_options,
#     shipping_dict = shipping_dict)
shipping_choices_query = django.dispatch.Signal()
