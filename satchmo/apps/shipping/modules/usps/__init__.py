import shipper
from livesettings import config_choice_values

def get_methods():
    return [shipper.Shipper(service_type=value) for value in config_choice_values('shipping.modules.usps', 'USPS_SHIPPING_CHOICES')]
