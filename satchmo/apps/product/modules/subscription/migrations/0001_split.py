# encoding: utf-8
from south.db import db
from south.v2 import SchemaMigration

class Migration(SchemaMigration):

    def forwards(self, orm):
        db.rename_table('product_subscriptionproduct', 'subscription_subscriptionproduct')
        db.rename_table('product_trial', 'subscription_trial')

    def backwards(self, orm):
        db.rename_table('subscription_subscriptionproduct', 'product_subscriptionproduct')
        db.rename_table('subscription_trial', 'product_trial')

    complete_apps = ['subscription']
