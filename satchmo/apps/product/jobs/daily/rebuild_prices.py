from django_extensions.management.jobs import DailyJob
from product.models import ProductPriceLookup

class Job(DailyJob):
    help = "Update the pricing lookup table."

    def execute(self):
        ProductPriceLookup.objects.rebuild_all()