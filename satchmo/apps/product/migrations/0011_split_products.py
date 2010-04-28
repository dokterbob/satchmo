# encoding: utf-8
from south.v2 import SchemaMigration

depends_on=(
    ('configurable', '0001_split'),
    ('custom', '0001_split'),
    ('downloadable', '0001_split'),
    ('subscription', '0001_split')
    )

class Migration(SchemaMigration):

    def forwards(self, orm):
        pass

    def backwards(self, orm):
        pass

    complete_apps = ['product']
