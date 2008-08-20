from django.db import models
from satchmo.configuration import config_value_safe

def payment_choices():
    try:
        return config_choice_values('PAYMENT', 'MODULES', translate=True)
    except SettingNotSet:
        return ()    

class PaymentChoiceCharField(models.CharField):
    
    def __init__(self, choices="__DYNAMIC__", *args, **kwargs):
        if choices == "__DYNAMIC__":
            kwargs['choices'] = payment_choices()
                    
        super(PaymentChoiceCharField, self).__init__(*args, **kwargs)