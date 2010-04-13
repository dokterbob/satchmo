# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        db.rename_table('product_customproduct', 'configurable_customproduct')
        db.rename_table('product_customtextfield', 'configurable_customtextfield')
        db.rename_table('product_customtextfieldtranslation', 'configurable_customtextfieldtranslation')
        db.rename_table('product_customproduct_option_group', 'configurable_customproduct_option_group')

    def backwards(self, orm):
        db.rename_table('configurable_customproduct', 'product_customproduct')
        db.rename_table('configurable_customtextfield', 'product_customtextfield')
        db.rename_table('configurable_customtextfieldtranslation', 'product_customtextfieldtranslation')
        db.rename_table('configurable_customproduct_option_group', 'product_customproduct_option_group')

    complete_apps = ['custom']
