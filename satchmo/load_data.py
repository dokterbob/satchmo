#!/usr/bin/env python

import urllib
from os.path import isdir, isfile, join, dirname
import os
import sys
import string
import csv
import tarfile
import shutil

if "DJANGO_SETTINGS_MODULE" not in os.environ:
    from settings import DJANGO_SETTINGS_MODULE
    os.environ["DJANGO_SETTINGS_MODULE"]=DJANGO_SETTINGS_MODULE

from django.conf import settings
from django.contrib.sites.models import Site
from django.contrib.auth.models import User
from django.core.management import call_command
from django.db import models
from satchmo.configuration import config_get_group

# Satchmo apps, sorted by their model dependencies.
satchmo_apps = [
    'satchmo.l10n',
    'satchmo.newsletter',
    'satchmo.tax',
    'satchmo.product',
    'satchmo.contact',
    'satchmo.discount',
    'satchmo.payment',
    'satchmo.supplier',
    'satchmo.shop']

def find_site():
    """Find the site by looking at the environment."""
    try:
        settings_module = os.environ['DJANGO_SETTINGS_MODULE']
    except KeyError:
        raise AssertionError("DJANGO_SETTINGS_MODULE not set.")

    settingsl = settings_module.split('.')
    site = __import__(settingsl[0])
    settings = __import__(settings_module, {}, {}, settingsl[-1])
    return site, settings

def delete_satchmo():
    """
    Delete all of the apps associated with Satchmo.
    """
    print("Deleting existing Satchmo data.")
    # Order the apps so that the apps with dependencies are deleted first.
    app_list = list(satchmo_apps)
    app_list.reverse()
    for app_name in app_list:
        if app_name in settings.INSTALLED_APPS:
            app = models.get_app(app_name.split('.')[-1], emptyOK=True)
            if app is not None:
                try:
                    print "Deleting %s" % app_name
                    call_command('reset', app_name.split('.')[-1], interactive=False)
                except:
                    print "Failed to delete application %s." % app_name

def delete_db(settings):
    """Delete the old database."""
    engine = settings.DATABASE_ENGINE
    if engine == 'sqlite3':
        try:
            os.unlink(settings.DATABASE_NAME)
        except OSError:
            pass
    elif engine == 'mysql':
        import _mysql
        s = _mysql.connect(host=settings.DATABASE_HOST,
                           user=settings.DATABASE_USER,
                           passwd=settings.DATABASE_PASSWORD)
        for cmd in ['drop database if exists %s',
                    'create database %s CHARACTER SET utf8 COLLATE utf8_general_ci']:
            s.query(cmd % settings.DATABASE_NAME)

    elif engine in ('postgresql', 'postgresql_psycopg2'):

        if settings.DATABASE_NAME == '':
            raise AssertionError("You must specify a value for DATABASE_NAME in local_settings.py.")
        if settings.DATABASE_USER == '':
            raise AssertionError("You must specify a value for DATABASE_USER in local_settings.py.")
        params=" --username=%s  --password" % settings.DATABASE_USER
        if settings.DATABASE_HOST:
            params += " --host=%s" % settings.DATABASE_HOST
        if settings.DATABASE_PORT:
            params += " --port=%s" % settings.DATABASE_PORT
        params += " %s" % settings.DATABASE_NAME
        print("""You will be prompted for the password for the user '%s' twice.
        Once to drop the existing database and then a second time to create
        the database.""" % settings.DATABASE_USER)
        for cmd in ['dropdb %s', 'createdb %s']:
            os.system(cmd % params)

    else:
        raise AssertionError("Unknown database engine %s" % engine)

def init_and_install():
    print("Calling syncdb")
    call_command('syncdb', interactive=True)
    call_command('loaddata', 'l10n_data.xml', interactive=True)

def load_data():
    from satchmo.contact.models import Contact, AddressBook, PhoneNumber
    from satchmo.product.models import Product, Price, ConfigurableProduct, ProductVariation, Category, OptionGroup, Option, ProductImage#, DownloadableProduct
    from satchmo.supplier.models import Organization
    from satchmo.shop.models import Config
    from django.conf import settings
    from satchmo.l10n.models import Country
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
    pg1.create_all_variations()
    pg3.create_all_variations()
    pg4.create_all_variations()
    #pg5.create_all_variations()

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


def eraseDB(all=False): 
    """Erase database and init it"""
    try: 
        site, settings = find_site()
        if all:
            delete_db(settings)
            print "All data successfully deleted."
        else:
            delete_satchmo()
            print "Satchmo data successfully deleted."
        init_and_install()
    except AssertionError, ex: 
        print ex.args[0]

def load_US_tax_table():
    """ Load a simple sales tax table for the US """
    from satchmo.tax.models import TaxRate, TaxClass
    from satchmo.l10n.models import AdminArea, Country
    us = Country.objects.get(iso2_code="US")
    defaultTax, created = TaxClass.objects.get_or_create(description="Default", title="Default")
    if created:
        defaultTax.save()
    dataFile = "tax-table.csv"
    dataDir = os.path.join(settings.DIRNAME,"tax/data")
    reader = csv.reader(open(os.path.join(dataDir, dataFile), "rb"))
    reader.next()       #Skip the header row
    for row in reader:
        state = AdminArea.objects.get(country=us, abbrev=row[0])
        stateTax = TaxRate(taxClass=defaultTax, taxZone=state, percentage=row[1])
        stateTax.save()        
    
if __name__ == '__main__': 
    response_erase_all = string.lower(raw_input("Type 'yes' to erase ALL data and reinstall ALL models: "))
    if response_erase_all == 'yes':
        eraseDB(all=True)
    else:
        response = string.lower(raw_input("Type 'yes' to erase any existing Satchmo data and reinstall all models: "))
        if response == 'yes':
            eraseDB(all=False)
    response = string.lower(raw_input("Type 'yes' to load sample store data: "))
    if response == 'yes':
        load_data()
    response = string.lower(raw_input("Type 'yes' to load a tax table for the US: "))
    if response == 'yes':
        load_US_tax_table()

   


