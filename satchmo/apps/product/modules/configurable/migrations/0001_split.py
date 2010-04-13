# encoding: utf-8
from south.db import db
from south.v2 import SchemaMigration

class Migration(SchemaMigration):

    def forwards(self, orm):
        db.rename_table('product_configurableproduct', 'configurable_configurableproduct')
        db.rename_table('product_productvariation', 'configurable_productvariation')
        db.rename_table('product_productvariation_options', 'configurable_productvariation_options')
        db.rename_table('product_configurableproduct_option_group', 'configurable_configurableproduct_option_group')

    def backwards(self, orm):
        db.rename_table('configurable_configurableproduct', 'product_configurableproduct')
        db.rename_table('configurable_productvariation', 'product_productvariation')
        db.rename_table('configurable_productvariation_options', 'product_productvariation_options')
        db.rename_table('configurable_configurableproduct_option_group', 'product_configurableproduct_option_group')

    complete_apps = ['configurable']
