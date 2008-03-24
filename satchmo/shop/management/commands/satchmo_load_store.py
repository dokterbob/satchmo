from django.core.management.base import NoArgsCommand

class Command(NoArgsCommand):
    help = "Load sample store data for satchmo."

    def handle_noargs(self, **options):
        print "Loading sample store data."
        from satchmo.contact.models import Contact, AddressBook, PhoneNumber
        from satchmo.product.models import Product, Price, ConfigurableProduct, ProductVariation, Category, OptionGroup, Option, ProductImage#, DownloadableProduct
        from satchmo.supplier.models import Organization
        from satchmo.shop.models import Config
        from django.conf import settings
        from satchmo.l10n.models import Country
        from django.contrib.sites.models import Site
        from django.contrib.auth.models import User
        #Load basic configuration information
        print "Creating site..."
        site = Site.objects.get(id=settings.SITE_ID)
        site.domain = settings.SITE_DOMAIN  
        site.name = settings.SITE_NAME
        site.save()
        store_country = Country.objects.get(iso3_code='USA')
        config = Config(site=site, store_name = settings.SITE_NAME, no_stock_checkout=False, country=store_country, sales_country=store_country)
        config.save()
        print "Creating Customers..."
        # Import some customers
        c1 = Contact(first_name="Chris", last_name="Smith", email="chris@aol.com", role="Customer", notes="Really cool stuff")
        c1.save()
        p1 = PhoneNumber(contact=c1, phone="601-555-5511", type="Home",primary=True)
        p1.save()
        c2 = Contact(first_name="John", last_name="Smith", email="abc@comcast.com", role="Customer", notes="Second user")
        c2.save()
        p2 = PhoneNumber(contact=c2, phone="999-555-5111", type="Work",primary=True)
        p2.save()
        # Import some addresses for these customers
        a1 = AddressBook(description="Home", street1="8235 Pike Street", city="Anywhere Town", state="TN",
                     postal_code="38138", country="US", is_default_shipping=True, contact=c1)
        a1.save()
        a2 = AddressBook(description="Work", street1="1245 Main Street", city="Stillwater", state="MN",
                     postal_code="55082", country="US", is_default_shipping=True, contact=c2)
        a2.save()
        print "Creating Suppliers..."
        #Import some suppliers
        org1 = Organization(name="Rhinestone Ronny", type="Company",role="Supplier")
        org1.save()
        c4 = Contact(first_name="Fred", last_name="Jones", email="fj@rr.com", role="Supplier", organization=org1)
        c4.save()
        p4 = PhoneNumber(contact=c4,phone="800-188-7611", type="Work", primary=True)
        p4.save()
        p5 = PhoneNumber(contact=c4,phone="755-555-1111",type="Fax")
        p5.save()
        a3 = AddressBook(contact=c4, description="Mailing address", street1="Receiving Dept", street2="918 Funky Town St", city="Fishkill",
                         state="NJ", postal_code="19010")
        a3.save()
        #s1 = Supplier(name="Rhinestone Ronny", address1="918 Funky Town St", address2="Suite 200",
        #              city="Fishkill", state="NJ", zip="19010", phone1="800-188-7611", fax="900-110-1909", email="ron@rhinestone.com",
        #              notes="My main supplier")
        #s1.save()

        #s2 = Supplier(name="Shirt Sally", address1="9 ABC Lane", 
        #    city="Happyville", state="MD", zip="190111", phone1="888-888-1111", fax="999-110-1909", email="sally@shirts.com",
        #              notes="Shirt Supplier")
        #s2.save()
        
        
        print "Creating Categories..."
        #Create some categories
        cat1 = Category(name="Shirts",slug="shirts",description="Women's Shirts")
        cat1.save()
        cat2 = Category(name="Short Sleeve",slug="shortsleeve",description="Short sleeve shirts", parent=cat1)
        cat2.save()
        cat3 = Category(name="Books",slug="book",description="Books")
        cat3.save()
        cat4 = Category(name="Fiction",slug="fiction",description="Fiction Books", parent=cat3)
        cat4.save()
        cat5 = Category(name="Science Fiction",slug="scifi",description="Science Fiction",parent=cat4)
        cat5.save()
        cat6 = Category(name="Non Fiction",slug="nonfiction",description="Non Fiction",parent=cat3)
        cat6.save()
        cat7 = Category(name="Software", slug="software")
        cat7.save()
        
        
        print "Creating products..."   
        #Create some items
        i1 = Product(name="Django Rocks shirt", slug="DJ-Rocks", description="Really cool shirt",
                 active=True, featured=True)
        i1.save()
        p1 = Price(price="20.00", product=i1)
        p1.save()
        i1.category.add(cat1)
        i1.save()
        i2 = Product(name="Python Rocks shirt", slug="PY-Rocks", description="Really cool python shirt - One Size Fits All", 
                 active=True, featured=True)
        i2.save()
        p2 = Price(price="19.50", product=i2)
        p2.save()
        i2.category.add(cat2)
        i2.save()
        i3 = Product(name="A really neat book", slug="neat-book", description="A neat book.  You should buy it.", 
                 active=True, featured=True)
        i3.save()
        p3 = Price(price="5.00", product=i3)
        p3.save()
        i3.category.add(cat4)
        i3.save()
        i4 = Product(name="Robots Attack!", slug="robot-attack", description="Robots try to take over the world.", 
                 active=True, featured=True)
        i4.save()
        p4 = Price(price="7.99", product=i4)
        p4.save()
        i4.category.add(cat5)
        i4.save()

    #    i5 = Product(name="Really Neat Software", slug="neat-software", description="Example Configurable/Downloadable product", active=True, featured=True)
    #    i5.save()
    #    i5.category.add(cat7)
    #    i5.save()

        #Create an attribute set 
        optSet1 = OptionGroup(name="sizes", sort_order=1)
        optSet2 = OptionGroup(name="colors", sort_order=2)
        optSet1.save()
        optSet2.save()
        
        optSet3 = OptionGroup(name="Book type", sort_order=1)
        optSet3.save()

        optSet4 = OptionGroup(name="Full/Upgrade", sort_order=5)
        optSet4.save()
        
        optItem1a = Option(name="Small", value="S", displayOrder=1, optionGroup=optSet1)
        optItem1a.save()
        optItem1b = Option(name="Medium", value="M", displayOrder=2, optionGroup=optSet1)
        optItem1b.save()
        optItem1c = Option(name="Large", value="L", displayOrder=3, price_change = 1.00, optionGroup=optSet1)
        optItem1c.save()

        optItem2a = Option(name="Black", value="B", displayOrder=1, optionGroup=optSet2)
        optItem2a.save()
        optItem2b = Option(name="White", value="W", displayOrder=2, optionGroup=optSet2)
        optItem2b.save()
        optItem2c = Option(name="Blue", value="BL", displayOrder=3, price_change=2.00, optionGroup=optSet2)
        optItem2c.save()

        optItem3a = Option(name="Hard cover", value="hard", displayOrder=1, optionGroup=optSet3)
        optItem3a.save()
        optItem3b = Option(name="Soft cover", value="soft", displayOrder=2, price_change=1.00, optionGroup=optSet3)
        optItem3b.save()
        optItem3c = Option(name="On tape", value="tape", displayOrder=3, optionGroup=optSet3)
        optItem3c.save()

        optItem4a = Option(name="Full Version", value="full", optionGroup=optSet4, displayOrder=1)
        optItem4a.save()
        optItem4b = Option(name="Upgrade Version", value="upgrade", optionGroup=optSet4, displayOrder=2)
        optItem4b.save()


        #Add the option group to our items
        pg1 = ConfigurableProduct(product=i1)
        pg1.save()
        pg1.option_group.add(optSet1)
        pg1.save()
        pg1.option_group.add(optSet2)
        pg1.save()

        pg3 = ConfigurableProduct(product=i3)
        pg3.save()
        pg3.option_group.add(optSet3)
        pg3.save()
        
        pg4 = ConfigurableProduct(product=i4)
        pg4.save()
        pg4.option_group.add(optSet3)
        pg4.save()

    #    pg5 = ConfigurableProduct(product=i5)
    #    pg5.option_group.add(optSet4)
    #    pg5.save()

        print "Creating product variations..."
        #Create the required sub_items
        pg1.create_products()
        pg3.create_products()
        pg4.create_products()
        #pg5.create_products()

        #set prices for full and upgrade versions of neat-software, this is an alternative to using the price_change in options, it allows for more flexability when required.
    #    pv1 = pg5.get_product_from_options([optItem4a])
    #    Price(product=pv1, price='5.00').save()
    #    Price(product=pv1, price='2.00', quantity=50).save()
    #    DownloadableProduct(product=pv1).save()

    #    pv2 = pg5.get_product_from_options([optItem4b])
    #    Price(product=pv2, price='1.00').save()
    #    DownloadableProduct(product=pv2).save()
        
        print "Create a test user..."
        #First see if our test user is still there, then use or create that user
        try:
            test_user = User.objects.get(username="csmith")
        except:
            test_user = User.objects.create_user('csmith', 'tester@testsite.com', 'test')
            test_user.save()
        c1.user = test_user
        c1.save()
