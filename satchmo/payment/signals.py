import django.dispatch

confirm_sanity_check = django.dispatch.Signal()
payment_form_init = django.dispatch.Signal()
payment_methods_query = django.dispatch.Signal()
form_save = django.dispatch.Signal()