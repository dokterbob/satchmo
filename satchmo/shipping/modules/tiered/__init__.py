from models import Carrier, Shipper
from satchmo.utils import load_once

load_once('tiered', 'satchmo.shipping.modules.tiered')

def get_methods():
    return [Shipper(carrier) for carrier in Carrier.objects.filter(active=True).order_by('ordering')]
