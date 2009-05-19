from django import forms
from django.db.models.fields import DecimalField
import logging
from widgets import CurrencyWidget

log = logging.getLogger('satchmo_utils.fields')

class CurrencyField(DecimalField):
    
    def __init__(self, *args, **kwargs):
        self.places = kwargs.pop('display_decimal', 2)
        super(CurrencyField, self).__init__(*args, **kwargs)

    def formfield(self, **kwargs):
        defaults = {
            'max_digits': self.max_digits,
            'decimal_places': self.decimal_places,
            'form_class': forms.DecimalField,
            'widget': CurrencyWidget,
        }
        defaults.update(kwargs)
        return super(CurrencyField, self).formfield(**defaults)
