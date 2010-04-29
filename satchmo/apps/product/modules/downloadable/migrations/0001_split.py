# encoding: utf-8
from south.db import db
from south.v2 import SchemaMigration

class Migration(SchemaMigration):

    def forwards(self, orm):
        db.rename_table('product_downloadableproduct', 'downloadable_downloadableproduct')
        db.rename_table('shop_downloadlink', 'downloadable_downloadlink')

    def backwards(self, orm):
        db.rename_table('downloadable_downloadableproduct', 'product_downloadableproduct')
        db.rename_table('downloadable_downloadlink', 'shop_downloadlink')

    complete_apps = ['downloadable']
