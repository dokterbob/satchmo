# encoding: utf-8
from south.db import db
from south.v2 import SchemaMigration

class Migration(SchemaMigration):

    def forwards(self, orm):
        db.rename_table('product_customproduct', 'custom_customproduct')
        db.rename_table('product_customproduct_option_group', 'custom_customproduct_option_group')
        db.rename_table('product_customtextfield', 'custom_customtextfield')
        db.rename_table('product_customtextfieldtranslation', 'custom_customtextfieldtranslation')

    def backwards(self, orm):
        db.rename_table('custom_customproduct', 'product_customproduct')
        db.rename_table('custom_customproduct_option_group', 'product_customproduct_option_group')
        db.rename_table('custom_customtextfield', 'product_customtextfield')
        db.rename_table('custom_customtextfieldtranslation', 'product_customtextfieldtranslation')

    complete_apps = ['custom']
