from django.contrib.sites.models import Site
from django.core.management.base import BaseCommand
from optparse import make_option
from product.models import Product, ProductPriceLookup

class Command(BaseCommand):
    help = "Builds Satcho Product pricing lookup tables."
    args = ['sitename...']

    requires_model_validation = True

    def handle(self, *sitenames, **options):
        from django.conf import settings

        verbosity = int(options.get('verbosity', 1))
        if len(sitenames) == 0:
            if verbosity>0:
                print "Rebuilding pricing for all products for all sites"
                sites = Site.objects.all()
        else:
            sites = []
            for sitename in sitenames:
                try:
                    sites.append(Site.objects.get(domain__iexact=sitename))
                except Site.DoesNotExist:
                    print "Warning: Could not find site '%s'" % sitename 

        total = 0
        for site in sites:
            ct = 0
            if verbosity > 0:
                print "Starting product pricing for %s" % site.domain

            if verbosity > 1:
                print "Deleting old pricing"
                
            for lookup in ProductPriceLookup.objects.filter(siteid=site.id):
                lookup.delete()
            
            products = Product.objects.active_by_site(site=site, variations=False)
            if verbosity > 0:
                print "Adding %i products" % products.count()
                
            for product in products:
                if verbosity > 1:
                    print "Processing product: %s" % product.slug
                
                prices = ProductPriceLookup.objects.smart_create_for_product(product)
                if verbosity > 1:
                    print "Created %i prices" % len(prices)
                
                ct += len(prices)
            
            if verbosity > 0:
                print "Added %i total prices for site" % ct
            
            total += ct

        if verbosity > 0:
            print "Added %i total prices" % total
            
