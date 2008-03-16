from django.utils.translation import ugettext_lazy as _
from django.core.validators import ValidationError

class MutuallyExclusiveWithField(object):
    def __init__(self, other_field_name, error_message=_("Please enter one and only one of those fields.")):
        self.other, self.error_message = other_field_name, error_message
        self.always_test = True

    def __call__(self, field_data, all_data):
        if all_data.get(self.other, False) and field_data or \
           not all_data.get(self.other, False) and not field_data:
            raise ValidationError, self.error_message

class ValidateIfFieldsSame(object):
    def __init__(self, other_field, error_message=_("These fields can not be the same.")):
        self.other_field = other_field
        self.always_test = True
        self.error_message = error_message
    
    def __call__(self, field_data, all_data):
        if field_data == all_data[self.other_field]:
            raise ValidationError, self.error_message