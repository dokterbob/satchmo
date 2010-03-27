# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):

        # Adding model 'Category'
        db.create_table('product_category', (
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('parent', self.gf('django.db.models.fields.related.ForeignKey')(related_name='child', blank=True, null=True, to=orm['product.Category'])),
            ('ordering', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('is_active', self.gf('django.db.models.fields.BooleanField')(default=True, blank=True)),
            ('site', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['sites.Site'])),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('meta', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('slug', self.gf('django.db.models.fields.SlugField')(db_index=True, max_length=50, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal('product', ['Category'])

        # Adding unique constraint on 'Category', fields ['site', 'slug']
        db.create_unique('product_category', ['site_id', 'slug'])

        # Adding M2M table for field related_categories on 'Category'
        db.create_table('product_category_related_categories', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('from_category', models.ForeignKey(orm['product.category'], null=False)),
            ('to_category', models.ForeignKey(orm['product.category'], null=False))
        ))
        db.create_unique('product_category_related_categories', ['from_category_id', 'to_category_id'])

        # Adding model 'CategoryTranslation'
        db.create_table('product_categorytranslation', (
            ('category', self.gf('django.db.models.fields.related.ForeignKey')(related_name='translations', to=orm['product.Category'])),
            ('languagecode', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('description', self.gf('django.db.models.fields.TextField')(default='', blank=True)),
            ('version', self.gf('django.db.models.fields.IntegerField')(default=1)),
            ('active', self.gf('django.db.models.fields.BooleanField')(default=True, blank=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal('product', ['CategoryTranslation'])

        # Adding unique constraint on 'CategoryTranslation', fields ['category', 'languagecode', 'version']
        db.create_unique('product_categorytranslation', ['category_id', 'languagecode', 'version'])

        # Adding model 'CategoryImage'
        db.create_table('product_categoryimage', (
            ('category', self.gf('django.db.models.fields.related.ForeignKey')(related_name='images', blank=True, null=True, to=orm['product.Category'])),
            ('picture', self.gf('satchmo_utils.thumbnail.field.ImageWithThumbnailField')(name_field='_filename', max_length=200)),
            ('sort', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('caption', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
        ))
        db.send_create_signal('product', ['CategoryImage'])

        # Adding unique constraint on 'CategoryImage', fields ['category', 'sort']
        db.create_unique('product_categoryimage', ['category_id', 'sort'])

        # Adding model 'CategoryImageTranslation'
        db.create_table('product_categoryimagetranslation', (
            ('languagecode', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('categoryimage', self.gf('django.db.models.fields.related.ForeignKey')(related_name='translations', to=orm['product.CategoryImage'])),
            ('caption', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('version', self.gf('django.db.models.fields.IntegerField')(default=1)),
            ('active', self.gf('django.db.models.fields.BooleanField')(default=True, blank=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('product', ['CategoryImageTranslation'])

        # Adding unique constraint on 'CategoryImageTranslation', fields ['categoryimage', 'languagecode', 'version']
        db.create_unique('product_categoryimagetranslation', ['categoryimage_id', 'languagecode', 'version'])

        # Adding model 'Discount'
        db.create_table('product_discount', (
            ('startDate', self.gf('django.db.models.fields.DateField')()),
            ('code', self.gf('django.db.models.fields.CharField')(max_length=20, unique=True)),
            ('endDate', self.gf('django.db.models.fields.DateField')()),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('numUses', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('allowedUses', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('site', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['sites.Site'])),
            ('shipping', self.gf('django.db.models.fields.CharField')(default='NONE', max_length=10, null=True, blank=True)),
            ('allValid', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('amount', self.gf('satchmo_utils.fields.CurrencyField')(null=True, max_digits=8, decimal_places=2, blank=True)),
            ('minOrder', self.gf('satchmo_utils.fields.CurrencyField')(null=True, max_digits=8, decimal_places=2, blank=True)),
            ('active', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('percentage', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=5, decimal_places=2, blank=True)),
            ('automatic', self.gf('django.db.models.fields.NullBooleanField')(default=False, null=True, blank=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('product', ['Discount'])

        # Adding M2M table for field validProducts on 'Discount'
        db.create_table('product_discount_validProducts', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('discount', models.ForeignKey(orm['product.discount'], null=False)),
            ('product', models.ForeignKey(orm['product.product'], null=False))
        ))
        db.create_unique('product_discount_validProducts', ['discount_id', 'product_id'])

        # Adding model 'OptionGroup'
        db.create_table('product_optiongroup', (
            ('description', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('sort_order', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('site', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['sites.Site'])),
        ))
        db.send_create_signal('product', ['OptionGroup'])

        # Adding model 'OptionGroupTranslation'
        db.create_table('product_optiongrouptranslation', (
            ('languagecode', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('description', self.gf('django.db.models.fields.TextField')(default='', blank=True)),
            ('version', self.gf('django.db.models.fields.IntegerField')(default=1)),
            ('active', self.gf('django.db.models.fields.BooleanField')(default=True, blank=True)),
            ('optiongroup', self.gf('django.db.models.fields.related.ForeignKey')(related_name='translations', to=orm['product.OptionGroup'])),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal('product', ['OptionGroupTranslation'])

        # Adding unique constraint on 'OptionGroupTranslation', fields ['optiongroup', 'languagecode', 'version']
        db.create_unique('product_optiongrouptranslation', ['optiongroup_id', 'languagecode', 'version'])

        # Adding model 'Option'
        db.create_table('product_option', (
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('price_change', self.gf('satchmo_utils.fields.CurrencyField')(null=True, max_digits=14, decimal_places=6, blank=True)),
            ('option_group', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['product.OptionGroup'])),
            ('value', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('sort_order', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('product', ['Option'])

        # Adding unique constraint on 'Option', fields ['option_group', 'value']
        db.create_unique('product_option', ['option_group_id', 'value'])

        # Adding model 'OptionTranslation'
        db.create_table('product_optiontranslation', (
            ('languagecode', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('version', self.gf('django.db.models.fields.IntegerField')(default=1)),
            ('active', self.gf('django.db.models.fields.BooleanField')(default=True, blank=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('option', self.gf('django.db.models.fields.related.ForeignKey')(related_name='translations', to=orm['product.Option'])),
        ))
        db.send_create_signal('product', ['OptionTranslation'])

        # Adding unique constraint on 'OptionTranslation', fields ['option', 'languagecode', 'version']
        db.create_unique('product_optiontranslation', ['option_id', 'languagecode', 'version'])

        # Adding model 'Product'
        db.create_table('product_product', (
            ('weight', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=8, decimal_places=2, blank=True)),
            ('site', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['sites.Site'])),
            ('height', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=6, decimal_places=2, blank=True)),
            ('taxable', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('featured', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('meta', self.gf('django.db.models.fields.TextField')(max_length=200, null=True, blank=True)),
            ('total_sold', self.gf('django.db.models.fields.DecimalField')(default='0', max_digits=18, decimal_places=6)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('sku', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('taxClass', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['product.TaxClass'], null=True, blank=True)),
            ('ordering', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('height_units', self.gf('django.db.models.fields.CharField')(max_length=3, null=True, blank=True)),
            ('width', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=6, decimal_places=2, blank=True)),
            ('items_in_stock', self.gf('django.db.models.fields.DecimalField')(default='0', max_digits=18, decimal_places=6)),
            ('short_description', self.gf('django.db.models.fields.TextField')(default='', max_length=200, blank=True)),
            ('length_units', self.gf('django.db.models.fields.CharField')(max_length=3, null=True, blank=True)),
            ('weight_units', self.gf('django.db.models.fields.CharField')(max_length=3, null=True, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(default='', blank=True)),
            ('active', self.gf('django.db.models.fields.BooleanField')(default=True, blank=True)),
            ('date_added', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('slug', self.gf('django.db.models.fields.SlugField')(db_index=True, max_length=255, blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('length', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=6, decimal_places=2, blank=True)),
            ('shipclass', self.gf('django.db.models.fields.CharField')(default='DEFAULT', max_length=10)),
            ('width_units', self.gf('django.db.models.fields.CharField')(max_length=3, null=True, blank=True)),
        ))
        db.send_create_signal('product', ['Product'])

        # Adding unique constraint on 'Product', fields ['site', 'sku']
        db.create_unique('product_product', ['site_id', 'sku'])

        # Adding unique constraint on 'Product', fields ['site', 'slug']
        db.create_unique('product_product', ['site_id', 'slug'])

        # Adding M2M table for field category on 'Product'
        db.create_table('product_product_category', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('product', models.ForeignKey(orm['product.product'], null=False)),
            ('category', models.ForeignKey(orm['product.category'], null=False))
        ))
        db.create_unique('product_product_category', ['product_id', 'category_id'])

        # Adding M2M table for field also_purchased on 'Product'
        db.create_table('product_product_also_purchased', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('from_product', models.ForeignKey(orm['product.product'], null=False)),
            ('to_product', models.ForeignKey(orm['product.product'], null=False))
        ))
        db.create_unique('product_product_also_purchased', ['from_product_id', 'to_product_id'])

        # Adding M2M table for field related_items on 'Product'
        db.create_table('product_product_related_items', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('from_product', models.ForeignKey(orm['product.product'], null=False)),
            ('to_product', models.ForeignKey(orm['product.product'], null=False))
        ))
        db.create_unique('product_product_related_items', ['from_product_id', 'to_product_id'])

        # Adding model 'ProductTranslation'
        db.create_table('product_producttranslation', (
            ('languagecode', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('product', self.gf('django.db.models.fields.related.ForeignKey')(related_name='translations', to=orm['product.Product'])),
            ('description', self.gf('django.db.models.fields.TextField')(default='', blank=True)),
            ('active', self.gf('django.db.models.fields.BooleanField')(default=True, blank=True)),
            ('version', self.gf('django.db.models.fields.IntegerField')(default=1)),
            ('short_description', self.gf('django.db.models.fields.TextField')(default='', max_length=200, blank=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal('product', ['ProductTranslation'])

        # Adding unique constraint on 'ProductTranslation', fields ['product', 'languagecode', 'version']
        db.create_unique('product_producttranslation', ['product_id', 'languagecode', 'version'])

        # Adding model 'CustomProduct'
        db.create_table('product_customproduct', (
            ('product', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['product.Product'], unique=True, primary_key=True)),
            ('deferred_shipping', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('downpayment', self.gf('django.db.models.fields.IntegerField')(default=20)),
        ))
        db.send_create_signal('product', ['CustomProduct'])

        # Adding M2M table for field option_group on 'CustomProduct'
        db.create_table('product_customproduct_option_group', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('customproduct', models.ForeignKey(orm['product.customproduct'], null=False)),
            ('optiongroup', models.ForeignKey(orm['product.optiongroup'], null=False))
        ))
        db.create_unique('product_customproduct_option_group', ['customproduct_id', 'optiongroup_id'])

        # Adding model 'CustomTextField'
        db.create_table('product_customtextfield', (
            ('name', self.gf('django.db.models.fields.CharField')(max_length=40)),
            ('price_change', self.gf('satchmo_utils.fields.CurrencyField')(null=True, max_digits=14, decimal_places=6, blank=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('sort_order', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('products', self.gf('django.db.models.fields.related.ForeignKey')(related_name='custom_text_fields', to=orm['product.CustomProduct'])),
            ('slug', self.gf('django.db.models.fields.SlugField')(db_index=True, max_length=50, blank=True)),
        ))
        db.send_create_signal('product', ['CustomTextField'])

        # Adding model 'CustomTextFieldTranslation'
        db.create_table('product_customtextfieldtranslation', (
            ('languagecode', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('version', self.gf('django.db.models.fields.IntegerField')(default=1)),
            ('active', self.gf('django.db.models.fields.BooleanField')(default=True, blank=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('customtextfield', self.gf('django.db.models.fields.related.ForeignKey')(related_name='translations', to=orm['product.CustomTextField'])),
        ))
        db.send_create_signal('product', ['CustomTextFieldTranslation'])

        # Adding unique constraint on 'CustomTextFieldTranslation', fields ['customtextfield', 'languagecode', 'version']
        db.create_unique('product_customtextfieldtranslation', ['customtextfield_id', 'languagecode', 'version'])

        # Adding model 'ConfigurableProduct'
        db.create_table('product_configurableproduct', (
            ('create_subs', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('product', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['product.Product'], unique=True, primary_key=True)),
        ))
        db.send_create_signal('product', ['ConfigurableProduct'])

        # Adding M2M table for field option_group on 'ConfigurableProduct'
        db.create_table('product_configurableproduct_option_group', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('configurableproduct', models.ForeignKey(orm['product.configurableproduct'], null=False)),
            ('optiongroup', models.ForeignKey(orm['product.optiongroup'], null=False))
        ))
        db.create_unique('product_configurableproduct_option_group', ['configurableproduct_id', 'optiongroup_id'])

        # Adding model 'DownloadableProduct'
        db.create_table('product_downloadableproduct', (
            ('active', self.gf('django.db.models.fields.BooleanField')(default=True, blank=True)),
            ('product', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['product.Product'], unique=True, primary_key=True)),
            ('num_allowed_downloads', self.gf('django.db.models.fields.IntegerField')()),
            ('file', self.gf('django.db.models.fields.files.FileField')(max_length=100)),
            ('expire_minutes', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('product', ['DownloadableProduct'])

        # Adding model 'SubscriptionProduct'
        db.create_table('product_subscriptionproduct', (
            ('product', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['product.Product'], unique=True, primary_key=True)),
            ('is_shippable', self.gf('django.db.models.fields.IntegerField')(max_length=1)),
            ('recurring_times', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('expire_unit', self.gf('django.db.models.fields.CharField')(default='DAY', max_length=5)),
            ('expire_length', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('recurring', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
        ))
        db.send_create_signal('product', ['SubscriptionProduct'])

        # Adding model 'Trial'
        db.create_table('product_trial', (
            ('expire_length', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('price', self.gf('satchmo_utils.fields.CurrencyField')(null=True, max_digits=10, decimal_places=2)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('subscription', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['product.SubscriptionProduct'])),
        ))
        db.send_create_signal('product', ['Trial'])

        # Adding model 'ProductVariation'
        db.create_table('product_productvariation', (
            ('product', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['product.Product'], unique=True, primary_key=True)),
            ('parent', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['product.ConfigurableProduct'])),
        ))
        db.send_create_signal('product', ['ProductVariation'])

        # Adding M2M table for field options on 'ProductVariation'
        db.create_table('product_productvariation_options', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('productvariation', models.ForeignKey(orm['product.productvariation'], null=False)),
            ('option', models.ForeignKey(orm['product.option'], null=False))
        ))
        db.create_unique('product_productvariation_options', ['productvariation_id', 'option_id'])

        # Adding model 'ProductPriceLookup'
        db.create_table('product_productpricelookup', (
            ('discountable', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('price', self.gf('django.db.models.fields.DecimalField')(max_digits=14, decimal_places=6)),
            ('items_in_stock', self.gf('django.db.models.fields.DecimalField')(max_digits=18, decimal_places=6)),
            ('siteid', self.gf('django.db.models.fields.IntegerField')()),
            ('key', self.gf('django.db.models.fields.CharField')(max_length=60, null=True)),
            ('parentid', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('active', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('productslug', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('quantity', self.gf('django.db.models.fields.DecimalField')(max_digits=18, decimal_places=6)),
        ))
        db.send_create_signal('product', ['ProductPriceLookup'])

        # Adding model 'ProductAttribute'
        db.create_table('product_productattribute', (
            ('languagecode', self.gf('django.db.models.fields.CharField')(max_length=10, null=True, blank=True)),
            ('product', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['product.Product'])),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('value', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('name', self.gf('django.db.models.fields.SlugField')(max_length=100, db_index=True)),
        ))
        db.send_create_signal('product', ['ProductAttribute'])

        # Adding model 'Price'
        db.create_table('product_price', (
            ('price', self.gf('satchmo_utils.fields.CurrencyField')(max_digits=14, decimal_places=6)),
            ('product', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['product.Product'])),
            ('expires', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('quantity', self.gf('django.db.models.fields.DecimalField')(default='1.0', max_digits=18, decimal_places=6)),
        ))
        db.send_create_signal('product', ['Price'])

        # Adding unique constraint on 'Price', fields ['product', 'quantity', 'expires']
        db.create_unique('product_price', ['product_id', 'quantity', 'expires'])

        # Adding model 'ProductImage'
        db.create_table('product_productimage', (
            ('sort', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('picture', self.gf('satchmo_utils.thumbnail.field.ImageWithThumbnailField')(name_field='_filename', max_length=200)),
            ('product', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['product.Product'], null=True, blank=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('caption', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
        ))
        db.send_create_signal('product', ['ProductImage'])

        # Adding model 'ProductImageTranslation'
        db.create_table('product_productimagetranslation', (
            ('languagecode', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('productimage', self.gf('django.db.models.fields.related.ForeignKey')(related_name='translations', to=orm['product.ProductImage'])),
            ('caption', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('version', self.gf('django.db.models.fields.IntegerField')(default=1)),
            ('active', self.gf('django.db.models.fields.BooleanField')(default=True, blank=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('product', ['ProductImageTranslation'])

        # Adding unique constraint on 'ProductImageTranslation', fields ['productimage', 'languagecode', 'version']
        db.create_unique('product_productimagetranslation', ['productimage_id', 'languagecode', 'version'])

        # Adding model 'TaxClass'
        db.create_table('product_taxclass', (
            ('description', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=20)),
        ))
        db.send_create_signal('product', ['TaxClass'])


    def backwards(self, orm):

        # Deleting model 'Category'
        db.delete_table('product_category')

        # Removing unique constraint on 'Category', fields ['site', 'slug']
        db.delete_unique('product_category', ['site_id', 'slug'])

        # Removing M2M table for field related_categories on 'Category'
        db.delete_table('product_category_related_categories')

        # Deleting model 'CategoryTranslation'
        db.delete_table('product_categorytranslation')

        # Removing unique constraint on 'CategoryTranslation', fields ['category', 'languagecode', 'version']
        db.delete_unique('product_categorytranslation', ['category_id', 'languagecode', 'version'])

        # Deleting model 'CategoryImage'
        db.delete_table('product_categoryimage')

        # Removing unique constraint on 'CategoryImage', fields ['category', 'sort']
        db.delete_unique('product_categoryimage', ['category_id', 'sort'])

        # Deleting model 'CategoryImageTranslation'
        db.delete_table('product_categoryimagetranslation')

        # Removing unique constraint on 'CategoryImageTranslation', fields ['categoryimage', 'languagecode', 'version']
        db.delete_unique('product_categoryimagetranslation', ['categoryimage_id', 'languagecode', 'version'])

        # Deleting model 'Discount'
        db.delete_table('product_discount')

        # Removing M2M table for field validProducts on 'Discount'
        db.delete_table('product_discount_validProducts')

        # Deleting model 'OptionGroup'
        db.delete_table('product_optiongroup')

        # Deleting model 'OptionGroupTranslation'
        db.delete_table('product_optiongrouptranslation')

        # Removing unique constraint on 'OptionGroupTranslation', fields ['optiongroup', 'languagecode', 'version']
        db.delete_unique('product_optiongrouptranslation', ['optiongroup_id', 'languagecode', 'version'])

        # Deleting model 'Option'
        db.delete_table('product_option')

        # Removing unique constraint on 'Option', fields ['option_group', 'value']
        db.delete_unique('product_option', ['option_group_id', 'value'])

        # Deleting model 'OptionTranslation'
        db.delete_table('product_optiontranslation')

        # Removing unique constraint on 'OptionTranslation', fields ['option', 'languagecode', 'version']
        db.delete_unique('product_optiontranslation', ['option_id', 'languagecode', 'version'])

        # Deleting model 'Product'
        db.delete_table('product_product')

        # Removing unique constraint on 'Product', fields ['site', 'sku']
        db.delete_unique('product_product', ['site_id', 'sku'])

        # Removing unique constraint on 'Product', fields ['site', 'slug']
        db.delete_unique('product_product', ['site_id', 'slug'])

        # Removing M2M table for field category on 'Product'
        db.delete_table('product_product_category')

        # Removing M2M table for field also_purchased on 'Product'
        db.delete_table('product_product_also_purchased')

        # Removing M2M table for field related_items on 'Product'
        db.delete_table('product_product_related_items')

        # Deleting model 'ProductTranslation'
        db.delete_table('product_producttranslation')

        # Removing unique constraint on 'ProductTranslation', fields ['product', 'languagecode', 'version']
        db.delete_unique('product_producttranslation', ['product_id', 'languagecode', 'version'])

        # Deleting model 'CustomProduct'
        db.delete_table('product_customproduct')

        # Removing M2M table for field option_group on 'CustomProduct'
        db.delete_table('product_customproduct_option_group')

        # Deleting model 'CustomTextField'
        db.delete_table('product_customtextfield')

        # Deleting model 'CustomTextFieldTranslation'
        db.delete_table('product_customtextfieldtranslation')

        # Removing unique constraint on 'CustomTextFieldTranslation', fields ['customtextfield', 'languagecode', 'version']
        db.delete_unique('product_customtextfieldtranslation', ['customtextfield_id', 'languagecode', 'version'])

        # Deleting model 'ConfigurableProduct'
        db.delete_table('product_configurableproduct')

        # Removing M2M table for field option_group on 'ConfigurableProduct'
        db.delete_table('product_configurableproduct_option_group')

        # Deleting model 'DownloadableProduct'
        db.delete_table('product_downloadableproduct')

        # Deleting model 'SubscriptionProduct'
        db.delete_table('product_subscriptionproduct')

        # Deleting model 'Trial'
        db.delete_table('product_trial')

        # Deleting model 'ProductVariation'
        db.delete_table('product_productvariation')

        # Removing M2M table for field options on 'ProductVariation'
        db.delete_table('product_productvariation_options')

        # Deleting model 'ProductPriceLookup'
        db.delete_table('product_productpricelookup')

        # Deleting model 'ProductAttribute'
        db.delete_table('product_productattribute')

        # Deleting model 'Price'
        db.delete_table('product_price')

        # Removing unique constraint on 'Price', fields ['product', 'quantity', 'expires']
        db.delete_unique('product_price', ['product_id', 'quantity', 'expires'])

        # Deleting model 'ProductImage'
        db.delete_table('product_productimage')

        # Deleting model 'ProductImageTranslation'
        db.delete_table('product_productimagetranslation')

        # Removing unique constraint on 'ProductImageTranslation', fields ['productimage', 'languagecode', 'version']
        db.delete_unique('product_productimagetranslation', ['productimage_id', 'languagecode', 'version'])

        # Deleting model 'TaxClass'
        db.delete_table('product_taxclass')


    models = {
        'product.category': {
            'Meta': {'unique_together': "(('site', 'slug'),)", 'object_name': 'Category'},
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'meta': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'ordering': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'child'", 'blank': 'True', 'null': 'True', 'to': "orm['product.Category']"}),
            'related_categories': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'related_categories'", 'blank': 'True', 'null': 'True', 'to': "orm['product.Category']"}),
            'site': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sites.Site']"}),
            'slug': ('django.db.models.fields.SlugField', [], {'db_index': 'True', 'max_length': '50', 'blank': 'True'})
        },
        'product.categoryimage': {
            'Meta': {'unique_together': "(('category', 'sort'),)", 'object_name': 'CategoryImage'},
            'caption': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'category': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'images'", 'blank': 'True', 'null': 'True', 'to': "orm['product.Category']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'picture': ('satchmo_utils.thumbnail.field.ImageWithThumbnailField', [], {'name_field': "'_filename'", 'max_length': '200'}),
            'sort': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        'product.categoryimagetranslation': {
            'Meta': {'unique_together': "(('categoryimage', 'languagecode', 'version'),)", 'object_name': 'CategoryImageTranslation'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'caption': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'categoryimage': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'translations'", 'to': "orm['product.CategoryImage']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'languagecode': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'version': ('django.db.models.fields.IntegerField', [], {'default': '1'})
        },
        'product.categorytranslation': {
            'Meta': {'unique_together': "(('category', 'languagecode', 'version'),)", 'object_name': 'CategoryTranslation'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'category': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'translations'", 'to': "orm['product.Category']"}),
            'description': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'languagecode': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'version': ('django.db.models.fields.IntegerField', [], {'default': '1'})
        },
        'product.configurableproduct': {
            'Meta': {'object_name': 'ConfigurableProduct'},
            'create_subs': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'option_group': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['product.OptionGroup']", 'blank': 'True'}),
            'product': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['product.Product']", 'unique': 'True', 'primary_key': 'True'})
        },
        'product.customproduct': {
            'Meta': {'object_name': 'CustomProduct'},
            'deferred_shipping': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'downpayment': ('django.db.models.fields.IntegerField', [], {'default': '20'}),
            'option_group': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['product.OptionGroup']", 'blank': 'True'}),
            'product': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['product.Product']", 'unique': 'True', 'primary_key': 'True'})
        },
        'product.customtextfield': {
            'Meta': {'object_name': 'CustomTextField'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'price_change': ('satchmo_utils.fields.CurrencyField', [], {'null': 'True', 'max_digits': '14', 'decimal_places': '6', 'blank': 'True'}),
            'products': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'custom_text_fields'", 'to': "orm['product.CustomProduct']"}),
            'slug': ('django.db.models.fields.SlugField', [], {'db_index': 'True', 'max_length': '50', 'blank': 'True'}),
            'sort_order': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        'product.customtextfieldtranslation': {
            'Meta': {'unique_together': "(('customtextfield', 'languagecode', 'version'),)", 'object_name': 'CustomTextFieldTranslation'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'customtextfield': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'translations'", 'to': "orm['product.CustomTextField']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'languagecode': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'version': ('django.db.models.fields.IntegerField', [], {'default': '1'})
        },
        'product.discount': {
            'Meta': {'object_name': 'Discount'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'allValid': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'allowedUses': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'amount': ('satchmo_utils.fields.CurrencyField', [], {'null': 'True', 'max_digits': '8', 'decimal_places': '2', 'blank': 'True'}),
            'automatic': ('django.db.models.fields.NullBooleanField', [], {'default': 'False', 'null': 'True', 'blank': 'True'}),
            'code': ('django.db.models.fields.CharField', [], {'max_length': '20', 'unique': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'endDate': ('django.db.models.fields.DateField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'minOrder': ('satchmo_utils.fields.CurrencyField', [], {'null': 'True', 'max_digits': '8', 'decimal_places': '2', 'blank': 'True'}),
            'numUses': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'percentage': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '5', 'decimal_places': '2', 'blank': 'True'}),
            'shipping': ('django.db.models.fields.CharField', [], {'default': "'NONE'", 'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'site': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sites.Site']"}),
            'startDate': ('django.db.models.fields.DateField', [], {}),
            'validProducts': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['product.Product']", 'null': 'True', 'blank': 'True'})
        },
        'product.downloadableproduct': {
            'Meta': {'object_name': 'DownloadableProduct'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'expire_minutes': ('django.db.models.fields.IntegerField', [], {}),
            'file': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            'num_allowed_downloads': ('django.db.models.fields.IntegerField', [], {}),
            'product': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['product.Product']", 'unique': 'True', 'primary_key': 'True'})
        },
        'product.option': {
            'Meta': {'unique_together': "(('option_group', 'value'),)", 'object_name': 'Option'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'option_group': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['product.OptionGroup']"}),
            'price_change': ('satchmo_utils.fields.CurrencyField', [], {'null': 'True', 'max_digits': '14', 'decimal_places': '6', 'blank': 'True'}),
            'sort_order': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'product.optiongroup': {
            'Meta': {'object_name': 'OptionGroup'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'site': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sites.Site']"}),
            'sort_order': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        'product.optiongrouptranslation': {
            'Meta': {'unique_together': "(('optiongroup', 'languagecode', 'version'),)", 'object_name': 'OptionGroupTranslation'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'languagecode': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'optiongroup': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'translations'", 'to': "orm['product.OptionGroup']"}),
            'version': ('django.db.models.fields.IntegerField', [], {'default': '1'})
        },
        'product.optiontranslation': {
            'Meta': {'unique_together': "(('option', 'languagecode', 'version'),)", 'object_name': 'OptionTranslation'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'languagecode': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'option': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'translations'", 'to': "orm['product.Option']"}),
            'version': ('django.db.models.fields.IntegerField', [], {'default': '1'})
        },
        'product.price': {
            'Meta': {'unique_together': "(('product', 'quantity', 'expires'),)", 'object_name': 'Price'},
            'expires': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'price': ('satchmo_utils.fields.CurrencyField', [], {'max_digits': '14', 'decimal_places': '6'}),
            'product': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['product.Product']"}),
            'quantity': ('django.db.models.fields.DecimalField', [], {'default': "'1.0'", 'max_digits': '18', 'decimal_places': '6'})
        },
        'product.product': {
            'Meta': {'unique_together': "(('site', 'sku'), ('site', 'slug'))", 'object_name': 'Product'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'also_purchased': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'also_products'", 'blank': 'True', 'null': 'True', 'to': "orm['product.Product']"}),
            'category': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['product.Category']", 'blank': 'True'}),
            'date_added': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'featured': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'height': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '6', 'decimal_places': '2', 'blank': 'True'}),
            'height_units': ('django.db.models.fields.CharField', [], {'max_length': '3', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'items_in_stock': ('django.db.models.fields.DecimalField', [], {'default': "'0'", 'max_digits': '18', 'decimal_places': '6'}),
            'length': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '6', 'decimal_places': '2', 'blank': 'True'}),
            'length_units': ('django.db.models.fields.CharField', [], {'max_length': '3', 'null': 'True', 'blank': 'True'}),
            'meta': ('django.db.models.fields.TextField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'ordering': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'related_items': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'related_products'", 'blank': 'True', 'null': 'True', 'to': "orm['product.Product']"}),
            'shipclass': ('django.db.models.fields.CharField', [], {'default': "'DEFAULT'", 'max_length': '10'}),
            'short_description': ('django.db.models.fields.TextField', [], {'default': "''", 'max_length': '200', 'blank': 'True'}),
            'site': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sites.Site']"}),
            'sku': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'db_index': 'True', 'max_length': '255', 'blank': 'True'}),
            'taxClass': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['product.TaxClass']", 'null': 'True', 'blank': 'True'}),
            'taxable': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'total_sold': ('django.db.models.fields.DecimalField', [], {'default': "'0'", 'max_digits': '18', 'decimal_places': '6'}),
            'weight': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '8', 'decimal_places': '2', 'blank': 'True'}),
            'weight_units': ('django.db.models.fields.CharField', [], {'max_length': '3', 'null': 'True', 'blank': 'True'}),
            'width': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '6', 'decimal_places': '2', 'blank': 'True'}),
            'width_units': ('django.db.models.fields.CharField', [], {'max_length': '3', 'null': 'True', 'blank': 'True'})
        },
        'product.productattribute': {
            'Meta': {'object_name': 'ProductAttribute'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'languagecode': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.SlugField', [], {'max_length': '100', 'db_index': 'True'}),
            'product': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['product.Product']"}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'product.productimage': {
            'Meta': {'object_name': 'ProductImage'},
            'caption': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'picture': ('satchmo_utils.thumbnail.field.ImageWithThumbnailField', [], {'name_field': "'_filename'", 'max_length': '200'}),
            'product': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['product.Product']", 'null': 'True', 'blank': 'True'}),
            'sort': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        'product.productimagetranslation': {
            'Meta': {'unique_together': "(('productimage', 'languagecode', 'version'),)", 'object_name': 'ProductImageTranslation'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'caption': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'languagecode': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'productimage': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'translations'", 'to': "orm['product.ProductImage']"}),
            'version': ('django.db.models.fields.IntegerField', [], {'default': '1'})
        },
        'product.productpricelookup': {
            'Meta': {'object_name': 'ProductPriceLookup'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'discountable': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'items_in_stock': ('django.db.models.fields.DecimalField', [], {'max_digits': '18', 'decimal_places': '6'}),
            'key': ('django.db.models.fields.CharField', [], {'max_length': '60', 'null': 'True'}),
            'parentid': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'price': ('django.db.models.fields.DecimalField', [], {'max_digits': '14', 'decimal_places': '6'}),
            'productslug': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'quantity': ('django.db.models.fields.DecimalField', [], {'max_digits': '18', 'decimal_places': '6'}),
            'siteid': ('django.db.models.fields.IntegerField', [], {})
        },
        'product.producttranslation': {
            'Meta': {'unique_together': "(('product', 'languagecode', 'version'),)", 'object_name': 'ProductTranslation'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'languagecode': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'product': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'translations'", 'to': "orm['product.Product']"}),
            'short_description': ('django.db.models.fields.TextField', [], {'default': "''", 'max_length': '200', 'blank': 'True'}),
            'version': ('django.db.models.fields.IntegerField', [], {'default': '1'})
        },
        'product.productvariation': {
            'Meta': {'object_name': 'ProductVariation'},
            'options': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['product.Option']"}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['product.ConfigurableProduct']"}),
            'product': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['product.Product']", 'unique': 'True', 'primary_key': 'True'})
        },
        'product.subscriptionproduct': {
            'Meta': {'object_name': 'SubscriptionProduct'},
            'expire_length': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'expire_unit': ('django.db.models.fields.CharField', [], {'default': "'DAY'", 'max_length': '5'}),
            'is_shippable': ('django.db.models.fields.IntegerField', [], {'max_length': '1'}),
            'product': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['product.Product']", 'unique': 'True', 'primary_key': 'True'}),
            'recurring': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'recurring_times': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        'product.taxclass': {
            'Meta': {'object_name': 'TaxClass'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '20'})
        },
        'product.trial': {
            'Meta': {'object_name': 'Trial'},
            'expire_length': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'price': ('satchmo_utils.fields.CurrencyField', [], {'null': 'True', 'max_digits': '10', 'decimal_places': '2'}),
            'subscription': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['product.SubscriptionProduct']"})
        },
        'sites.site': {
            'Meta': {'object_name': 'Site', 'db_table': "'django_site'"},
            'domain': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        }
    }

    complete_apps = ['product']
