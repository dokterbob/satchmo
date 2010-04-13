# encoding: utf-8
from south.db import db
from south.v2 import SchemaMigration

class Migration(SchemaMigration):

    def forwards(self, orm):
        db.rename_table('product_configurableproduct', 'configurable_configurableproduct')

    def backwards(self, orm):
        db.rename_table('configurable_configurableproduct', 'product_configurableproduct')

    complete_apps = ['configurable']
