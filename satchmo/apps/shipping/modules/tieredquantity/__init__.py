from models import Carrier, Shipper

def get_methods():
    return [Shipper(carrier) for carrier in Carrier.objects.filter(active=True).order_by('ordering')]

