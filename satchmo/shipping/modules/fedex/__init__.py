import shipper
from satchmo.configuration import config_choice_values

def get_methods():
  '''
    Fires off shipper.Shipper() for each choice that's
    enabled in /settings/
  '''

  return [shipper.Shipper(service_type=value) for value in config_choice_values('satchmo.shipping.modules.fedex', 'SHIPPING_CHOICES')]
