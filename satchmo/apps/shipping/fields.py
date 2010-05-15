from django.db import models
from livesettings import config_value_safe

def shipping_choices():
    try:
        return config_choice_values('SHIPPING','MODULES')
    except SettingNotSet:
        return ()


class ShippingChoiceCharField(models.CharField):

    def __init__(self, choices="__DYNAMIC__", *args, **kwargs):
        if choices == "__DYNAMIC__":
            kwargs['choices'] = shipping_choices()

        super(ShippingChoiceCharField, self).__init__(*args, **kwargs)

try:
    # South introspection rules for our custom field.
    from south.modelsinspector import add_introspection_rules, matching_details

    # get the kwargs for a Field instance
    # we're using Field, as CharField doesn't change __init__()
    _args, kwargs = matching_details(models.Field())

    add_introspection_rules([(
        (ShippingChoiceCharField, ),
        [],
        kwargs,
    )], ['shipping\.fields'])
except ImportError:
    pass
