# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        db.rename_table('product_subscriptionproduct', 'subscription_subscriptionproduct')
        db.rename_table('product_trial', 'subscription_trial')

    def backwards(self, orm):
        db.rename_table('subscription_subscriptionproduct', 'product_subscriptionproduct')
        db.rename_table('subscription_trial', 'product_trial')

    complete_apps = ['subscription']
