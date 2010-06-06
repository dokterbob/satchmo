from django.contrib.contenttypes.models import ContentType
from south.logger import get_logger
from south.v2 import DataMigration

# Helper class for (0012|0002)_update_content_types
class UpdateContentTypeMigration(DataMigration):
    _app_label = None

    def __init__(self, *args, **kwargs):
        super(UpdateContentTypeMigration, self).__init__(*args, **kwargs)

        # find a list of models used in this product module from the frozen orm
        models = []
        for model in self.models.keys():
            try:
                i = model.index(self._app_label)
                models.append(model[len(self._app_label)+1:])
            except ValueError:
                continue
        self._models = models

    def migrate_contenttype(self, from_app, to_app):
        # ideally, we should have frozen content types too, but we're lazy.
        q = ContentType.objects.filter(
            app_label=from_app,
            model__in=self._models,
        )

        # sanity check; just warn, don't have to error out
        if not len(q) == len(self._models):
            get_logger().warning(
                "Not all content types for models (%s) in app %s were found" % \
                    (self._models, from_app))

        for ct in q:
            ct.app_label = to_app
            ct.save()

    def forwards(self, filter):
        self.migrate_contenttype('product', self._app_label)

    def backwards(self, filter):
        self.migrate_contenttype(self._app_label, 'product')
