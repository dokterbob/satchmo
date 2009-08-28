import django.dispatch

confirm_sanity_check = django.dispatch.Signal()
payment_choices = django.dispatch.Signal()
payment_methods_query = django.dispatch.Signal()
