from django.db import models
from livesettings import config_value_safe, config_choice_values
from payment.config import credit_choices, labelled_payment_choices

class CreditChoiceCharField(models.CharField):

    def __init__(self, choices="__DYNAMIC__", *args, **kwargs):
        if choices == "__DYNAMIC__":
            kwargs['choices'] = credit_choices()

        super(CreditChoiceCharField, self).__init__(*args, **kwargs)

class PaymentChoiceCharField(models.CharField):
    
    def __init__(self, choices="__DYNAMIC__", *args, **kwargs):
        if choices == "__DYNAMIC__":
            kwargs['choices'] = labelled_payment_choices()
                    
        super(PaymentChoiceCharField, self).__init__(*args, **kwargs)
