
from south.db import db
from django.db import models
from product.models import *

class Migration:
    
    def forwards(self, orm):
        
        # Adding model 'CategoryTranslation'
        db.create_table('product_categorytranslation', (
            ('id', orm['product.CategoryTranslation:id']),
            ('category', orm['product.CategoryTranslation:category']),
            ('languagecode', orm['product.CategoryTranslation:languagecode']),
            ('name', orm['product.CategoryTranslation:name']),
            ('description', orm['product.CategoryTranslation:description']),
            ('version', orm['product.CategoryTranslation:version']),
            ('active', orm['product.CategoryTranslation:active']),
        ))
        db.send_create_signal('product', ['CategoryTranslation'])
        
        # Adding model 'ProductAttribute'
        db.create_table('product_productattribute', (
            ('id', orm['product.ProductAttribute:id']),
            ('product', orm['product.ProductAttribute:product']),
            ('languagecode', orm['product.ProductAttribute:languagecode']),
            ('name', orm['product.ProductAttribute:name']),
            ('value', orm['product.ProductAttribute:value']),
        ))
        db.send_create_signal('product', ['ProductAttribute'])
        
        # Adding model 'TaxClass'
        db.create_table('product_taxclass', (
            ('id', orm['product.TaxClass:id']),
            ('title', orm['product.TaxClass:title']),
            ('description', orm['product.TaxClass:description']),
        ))
        db.send_create_signal('product', ['TaxClass'])
        
        # Adding model 'CategoryImageTranslation'
        db.create_table('product_categoryimagetranslation', (
            ('id', orm['product.CategoryImageTranslation:id']),
            ('categoryimage', orm['product.CategoryImageTranslation:categoryimage']),
            ('languagecode', orm['product.CategoryImageTranslation:languagecode']),
            ('caption', orm['product.CategoryImageTranslation:caption']),
            ('version', orm['product.CategoryImageTranslation:version']),
            ('active', orm['product.CategoryImageTranslation:active']),
        ))
        db.send_create_signal('product', ['CategoryImageTranslation'])
        
        # Adding model 'Trial'
        db.create_table('product_trial', (
            ('id', orm['product.Trial:id']),
            ('subscription', orm['product.Trial:subscription']),
            ('price', orm['product.Trial:price']),
            ('expire_length', orm['product.Trial:expire_length']),
        ))
        db.send_create_signal('product', ['Trial'])
        
        # Adding model 'ProductVariation'
        db.create_table('product_productvariation', (
            ('product', orm['product.ProductVariation:product']),
            ('parent', orm['product.ProductVariation:parent']),
        ))
        db.send_create_signal('product', ['ProductVariation'])
        
        # Adding model 'CustomTextField'
        db.create_table('product_customtextfield', (
            ('id', orm['product.CustomTextField:id']),
            ('name', orm['product.CustomTextField:name']),
            ('slug', orm['product.CustomTextField:slug']),
            ('products', orm['product.CustomTextField:products']),
            ('sort_order', orm['product.CustomTextField:sort_order']),
            ('price_change', orm['product.CustomTextField:price_change']),
        ))
        db.send_create_signal('product', ['CustomTextField'])
        
        # Adding model 'Category'
        db.create_table('product_category', (
            ('id', orm['product.Category:id']),
            ('site', orm['product.Category:site']),
            ('name', orm['product.Category:name']),
            ('slug', orm['product.Category:slug']),
            ('parent', orm['product.Category:parent']),
            ('meta', orm['product.Category:meta']),
            ('description', orm['product.Category:description']),
            ('ordering', orm['product.Category:ordering']),
            ('is_active', orm['product.Category:is_active']),
        ))
        db.send_create_signal('product', ['Category'])
        
        # Adding model 'CategoryImage'
        db.create_table('product_categoryimage', (
            ('id', orm['product.CategoryImage:id']),
            ('category', orm['product.CategoryImage:category']),
            ('picture', orm['product.CategoryImage:picture']),
            ('caption', orm['product.CategoryImage:caption']),
            ('sort', orm['product.CategoryImage:sort']),
        ))
        db.send_create_signal('product', ['CategoryImage'])
        
        # Adding model 'CustomTextFieldTranslation'
        db.create_table('product_customtextfieldtranslation', (
            ('id', orm['product.CustomTextFieldTranslation:id']),
            ('customtextfield', orm['product.CustomTextFieldTranslation:customtextfield']),
            ('languagecode', orm['product.CustomTextFieldTranslation:languagecode']),
            ('name', orm['product.CustomTextFieldTranslation:name']),
            ('version', orm['product.CustomTextFieldTranslation:version']),
            ('active', orm['product.CustomTextFieldTranslation:active']),
        ))
        db.send_create_signal('product', ['CustomTextFieldTranslation'])
        
        # Adding model 'ProductPriceLookup'
        db.create_table('product_productpricelookup', (
            ('id', orm['product.ProductPriceLookup:id']),
            ('siteid', orm['product.ProductPriceLookup:siteid']),
            ('key', orm['product.ProductPriceLookup:key']),
            ('parentid', orm['product.ProductPriceLookup:parentid']),
            ('productslug', orm['product.ProductPriceLookup:productslug']),
            ('price', orm['product.ProductPriceLookup:price']),
            ('quantity', orm['product.ProductPriceLookup:quantity']),
            ('active', orm['product.ProductPriceLookup:active']),
            ('discountable', orm['product.ProductPriceLookup:discountable']),
            ('items_in_stock', orm['product.ProductPriceLookup:items_in_stock']),
        ))
        db.send_create_signal('product', ['ProductPriceLookup'])
        
        # Adding model 'Price'
        db.create_table('product_price', (
            ('id', orm['product.Price:id']),
            ('product', orm['product.Price:product']),
            ('price', orm['product.Price:price']),
            ('quantity', orm['product.Price:quantity']),
            ('expires', orm['product.Price:expires']),
        ))
        db.send_create_signal('product', ['Price'])
        
        # Adding model 'ConfigurableProduct'
        db.create_table('product_configurableproduct', (
            ('product', orm['product.ConfigurableProduct:product']),
            ('create_subs', orm['product.ConfigurableProduct:create_subs']),
        ))
        db.send_create_signal('product', ['ConfigurableProduct'])
        
        # Adding model 'OptionTranslation'
        db.create_table('product_optiontranslation', (
            ('id', orm['product.OptionTranslation:id']),
            ('option', orm['product.OptionTranslation:option']),
            ('languagecode', orm['product.OptionTranslation:languagecode']),
            ('name', orm['product.OptionTranslation:name']),
            ('version', orm['product.OptionTranslation:version']),
            ('active', orm['product.OptionTranslation:active']),
        ))
        db.send_create_signal('product', ['OptionTranslation'])
        
        # Adding model 'Discount'
        db.create_table('product_discount', (
            ('id', orm['product.Discount:id']),
            ('site', orm['product.Discount:site']),
            ('description', orm['product.Discount:description']),
            ('code', orm['product.Discount:code']),
            ('active', orm['product.Discount:active']),
            ('amount', orm['product.Discount:amount']),
            ('percentage', orm['product.Discount:percentage']),
            ('automatic', orm['product.Discount:automatic']),
            ('allowedUses', orm['product.Discount:allowedUses']),
            ('numUses', orm['product.Discount:numUses']),
            ('minOrder', orm['product.Discount:minOrder']),
            ('startDate', orm['product.Discount:startDate']),
            ('endDate', orm['product.Discount:endDate']),
            ('shipping', orm['product.Discount:shipping']),
            ('allValid', orm['product.Discount:allValid']),
        ))
        db.send_create_signal('product', ['Discount'])
        
        # Adding model 'DownloadableProduct'
        db.create_table('product_downloadableproduct', (
            ('product', orm['product.DownloadableProduct:product']),
            ('file', orm['product.DownloadableProduct:file']),
            ('num_allowed_downloads', orm['product.DownloadableProduct:num_allowed_downloads']),
            ('expire_minutes', orm['product.DownloadableProduct:expire_minutes']),
            ('active', orm['product.DownloadableProduct:active']),
        ))
        db.send_create_signal('product', ['DownloadableProduct'])
        
        # Adding model 'OptionGroup'
        db.create_table('product_optiongroup', (
            ('id', orm['product.OptionGroup:id']),
            ('site', orm['product.OptionGroup:site']),
            ('name', orm['product.OptionGroup:name']),
            ('description', orm['product.OptionGroup:description']),
            ('sort_order', orm['product.OptionGroup:sort_order']),
        ))
        db.send_create_signal('product', ['OptionGroup'])
        
        # Adding model 'CustomProduct'
        db.create_table('product_customproduct', (
            ('product', orm['product.CustomProduct:product']),
            ('downpayment', orm['product.CustomProduct:downpayment']),
            ('deferred_shipping', orm['product.CustomProduct:deferred_shipping']),
        ))
        db.send_create_signal('product', ['CustomProduct'])
        
        # Adding model 'Product'
        db.create_table('product_product', (
            ('id', orm['product.Product:id']),
            ('site', orm['product.Product:site']),
            ('name', orm['product.Product:name']),
            ('slug', orm['product.Product:slug']),
            ('sku', orm['product.Product:sku']),
            ('short_description', orm['product.Product:short_description']),
            ('description', orm['product.Product:description']),
            ('items_in_stock', orm['product.Product:items_in_stock']),
            ('meta', orm['product.Product:meta']),
            ('date_added', orm['product.Product:date_added']),
            ('active', orm['product.Product:active']),
            ('featured', orm['product.Product:featured']),
            ('ordering', orm['product.Product:ordering']),
            ('weight', orm['product.Product:weight']),
            ('weight_units', orm['product.Product:weight_units']),
            ('length', orm['product.Product:length']),
            ('length_units', orm['product.Product:length_units']),
            ('width', orm['product.Product:width']),
            ('width_units', orm['product.Product:width_units']),
            ('height', orm['product.Product:height']),
            ('height_units', orm['product.Product:height_units']),
            ('total_sold', orm['product.Product:total_sold']),
            ('taxable', orm['product.Product:taxable']),
            ('taxClass', orm['product.Product:taxClass']),
            ('shipclass', orm['product.Product:shipclass']),
        ))
        db.send_create_signal('product', ['Product'])
        
        # Adding model 'ProductImageTranslation'
        db.create_table('product_productimagetranslation', (
            ('id', orm['product.ProductImageTranslation:id']),
            ('productimage', orm['product.ProductImageTranslation:productimage']),
            ('languagecode', orm['product.ProductImageTranslation:languagecode']),
            ('caption', orm['product.ProductImageTranslation:caption']),
            ('version', orm['product.ProductImageTranslation:version']),
            ('active', orm['product.ProductImageTranslation:active']),
        ))
        db.send_create_signal('product', ['ProductImageTranslation'])
        
        # Adding model 'OptionGroupTranslation'
        db.create_table('product_optiongrouptranslation', (
            ('id', orm['product.OptionGroupTranslation:id']),
            ('optiongroup', orm['product.OptionGroupTranslation:optiongroup']),
            ('languagecode', orm['product.OptionGroupTranslation:languagecode']),
            ('name', orm['product.OptionGroupTranslation:name']),
            ('description', orm['product.OptionGroupTranslation:description']),
            ('version', orm['product.OptionGroupTranslation:version']),
            ('active', orm['product.OptionGroupTranslation:active']),
        ))
        db.send_create_signal('product', ['OptionGroupTranslation'])
        
        # Adding model 'ProductImage'
        db.create_table('product_productimage', (
            ('id', orm['product.ProductImage:id']),
            ('product', orm['product.ProductImage:product']),
            ('picture', orm['product.ProductImage:picture']),
            ('caption', orm['product.ProductImage:caption']),
            ('sort', orm['product.ProductImage:sort']),
        ))
        db.send_create_signal('product', ['ProductImage'])
        
        # Adding model 'Option'
        db.create_table('product_option', (
            ('id', orm['product.Option:id']),
            ('option_group', orm['product.Option:option_group']),
            ('name', orm['product.Option:name']),
            ('value', orm['product.Option:value']),
            ('price_change', orm['product.Option:price_change']),
            ('sort_order', orm['product.Option:sort_order']),
        ))
        db.send_create_signal('product', ['Option'])
        
        # Adding model 'SubscriptionProduct'
        db.create_table('product_subscriptionproduct', (
            ('product', orm['product.SubscriptionProduct:product']),
            ('recurring', orm['product.SubscriptionProduct:recurring']),
            ('recurring_times', orm['product.SubscriptionProduct:recurring_times']),
            ('expire_length', orm['product.SubscriptionProduct:expire_length']),
            ('expire_unit', orm['product.SubscriptionProduct:expire_unit']),
            ('is_shippable', orm['product.SubscriptionProduct:is_shippable']),
        ))
        db.send_create_signal('product', ['SubscriptionProduct'])
        
        # Adding model 'ProductTranslation'
        db.create_table('product_producttranslation', (
            ('id', orm['product.ProductTranslation:id']),
            ('product', orm['product.ProductTranslation:product']),
            ('languagecode', orm['product.ProductTranslation:languagecode']),
            ('name', orm['product.ProductTranslation:name']),
            ('description', orm['product.ProductTranslation:description']),
            ('short_description', orm['product.ProductTranslation:short_description']),
            ('version', orm['product.ProductTranslation:version']),
            ('active', orm['product.ProductTranslation:active']),
        ))
        db.send_create_signal('product', ['ProductTranslation'])
        
        # Adding ManyToManyField 'Category.related_categories'
        db.create_table('product_category_related_categories', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('from_category', models.ForeignKey(orm.Category, null=False)),
            ('to_category', models.ForeignKey(orm.Category, null=False))
        ))
        
        # Adding ManyToManyField 'ConfigurableProduct.option_group'
        db.create_table('product_configurableproduct_option_group', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('configurableproduct', models.ForeignKey(orm.ConfigurableProduct, null=False)),
            ('optiongroup', models.ForeignKey(orm.OptionGroup, null=False))
        ))
        
        # Adding ManyToManyField 'ProductVariation.options'
        db.create_table('product_productvariation_options', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('productvariation', models.ForeignKey(orm.ProductVariation, null=False)),
            ('option', models.ForeignKey(orm.Option, null=False))
        ))
        
        # Adding ManyToManyField 'CustomProduct.option_group'
        db.create_table('product_customproduct_option_group', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('customproduct', models.ForeignKey(orm.CustomProduct, null=False)),
            ('optiongroup', models.ForeignKey(orm.OptionGroup, null=False))
        ))
        
        # Adding ManyToManyField 'Product.also_purchased'
        db.create_table('product_product_also_purchased', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('from_product', models.ForeignKey(orm.Product, null=False)),
            ('to_product', models.ForeignKey(orm.Product, null=False))
        ))
        
        # Adding ManyToManyField 'Discount.validProducts'
        db.create_table('product_discount_validProducts', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('discount', models.ForeignKey(orm.Discount, null=False)),
            ('product', models.ForeignKey(orm.Product, null=False))
        ))
        
        # Adding ManyToManyField 'Product.related_items'
        db.create_table('product_product_related_items', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('from_product', models.ForeignKey(orm.Product, null=False)),
            ('to_product', models.ForeignKey(orm.Product, null=False))
        ))
        
        # Adding ManyToManyField 'Product.category'
        db.create_table('product_product_category', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('product', models.ForeignKey(orm.Product, null=False)),
            ('category', models.ForeignKey(orm.Category, null=False))
        ))
        
        # Creating unique_together for [product, languagecode, version] on ProductTranslation.
        db.create_unique('product_producttranslation', ['product_id', 'languagecode', 'version'])
        
        # Creating unique_together for [site, slug] on Product.
        db.create_unique('product_product', ['site_id', 'slug'])
        
        # Creating unique_together for [category, sort] on CategoryImage.
        db.create_unique('product_categoryimage', ['category_id', 'sort'])
        
        # Creating unique_together for [option_group, value] on Option.
        db.create_unique('product_option', ['option_group_id', 'value'])
        
        # Creating unique_together for [product, quantity, expires] on Price.
        db.create_unique('product_price', ['product_id', 'quantity', 'expires'])
        
        # Creating unique_together for [productimage, languagecode, version] on ProductImageTranslation.
        db.create_unique('product_productimagetranslation', ['productimage_id', 'languagecode', 'version'])
        
        # Creating unique_together for [site, slug] on Category.
        db.create_unique('product_category', ['site_id', 'slug'])
        
        # Creating unique_together for [categoryimage, languagecode, version] on CategoryImageTranslation.
        db.create_unique('product_categoryimagetranslation', ['categoryimage_id', 'languagecode', 'version'])
        
        # Creating unique_together for [option, languagecode, version] on OptionTranslation.
        db.create_unique('product_optiontranslation', ['option_id', 'languagecode', 'version'])
        
        # Creating unique_together for [optiongroup, languagecode, version] on OptionGroupTranslation.
        db.create_unique('product_optiongrouptranslation', ['optiongroup_id', 'languagecode', 'version'])
        
        # Creating unique_together for [category, languagecode, version] on CategoryTranslation.
        db.create_unique('product_categorytranslation', ['category_id', 'languagecode', 'version'])
        
        # Creating unique_together for [site, sku] on Product.
        db.create_unique('product_product', ['site_id', 'sku'])
        
        # Creating unique_together for [customtextfield, languagecode, version] on CustomTextFieldTranslation.
        db.create_unique('product_customtextfieldtranslation', ['customtextfield_id', 'languagecode', 'version'])
        
    
    
    def backwards(self, orm):
        
        # Deleting unique_together for [customtextfield, languagecode, version] on CustomTextFieldTranslation.
        db.delete_unique('product_customtextfieldtranslation', ['customtextfield_id', 'languagecode', 'version'])
        
        # Deleting unique_together for [site, sku] on Product.
        db.delete_unique('product_product', ['site_id', 'sku'])
        
        # Deleting unique_together for [category, languagecode, version] on CategoryTranslation.
        db.delete_unique('product_categorytranslation', ['category_id', 'languagecode', 'version'])
        
        # Deleting unique_together for [optiongroup, languagecode, version] on OptionGroupTranslation.
        db.delete_unique('product_optiongrouptranslation', ['optiongroup_id', 'languagecode', 'version'])
        
        # Deleting unique_together for [option, languagecode, version] on OptionTranslation.
        db.delete_unique('product_optiontranslation', ['option_id', 'languagecode', 'version'])
        
        # Deleting unique_together for [categoryimage, languagecode, version] on CategoryImageTranslation.
        db.delete_unique('product_categoryimagetranslation', ['categoryimage_id', 'languagecode', 'version'])
        
        # Deleting unique_together for [site, slug] on Category.
        db.delete_unique('product_category', ['site_id', 'slug'])
        
        # Deleting unique_together for [productimage, languagecode, version] on ProductImageTranslation.
        db.delete_unique('product_productimagetranslation', ['productimage_id', 'languagecode', 'version'])
        
        # Deleting unique_together for [product, quantity, expires] on Price.
        db.delete_unique('product_price', ['product_id', 'quantity', 'expires'])
        
        # Deleting unique_together for [option_group, value] on Option.
        db.delete_unique('product_option', ['option_group_id', 'value'])
        
        # Deleting unique_together for [category, sort] on CategoryImage.
        db.delete_unique('product_categoryimage', ['category_id', 'sort'])
        
        # Deleting unique_together for [site, slug] on Product.
        db.delete_unique('product_product', ['site_id', 'slug'])
        
        # Deleting unique_together for [product, languagecode, version] on ProductTranslation.
        db.delete_unique('product_producttranslation', ['product_id', 'languagecode', 'version'])
        
        # Deleting model 'CategoryTranslation'
        db.delete_table('product_categorytranslation')
        
        # Deleting model 'ProductAttribute'
        db.delete_table('product_productattribute')
        
        # Deleting model 'TaxClass'
        db.delete_table('product_taxclass')
        
        # Deleting model 'CategoryImageTranslation'
        db.delete_table('product_categoryimagetranslation')
        
        # Deleting model 'Trial'
        db.delete_table('product_trial')
        
        # Deleting model 'ProductVariation'
        db.delete_table('product_productvariation')
        
        # Deleting model 'CustomTextField'
        db.delete_table('product_customtextfield')
        
        # Deleting model 'Category'
        db.delete_table('product_category')
        
        # Deleting model 'CategoryImage'
        db.delete_table('product_categoryimage')
        
        # Deleting model 'CustomTextFieldTranslation'
        db.delete_table('product_customtextfieldtranslation')
        
        # Deleting model 'ProductPriceLookup'
        db.delete_table('product_productpricelookup')
        
        # Deleting model 'Price'
        db.delete_table('product_price')
        
        # Deleting model 'ConfigurableProduct'
        db.delete_table('product_configurableproduct')
        
        # Deleting model 'OptionTranslation'
        db.delete_table('product_optiontranslation')
        
        # Deleting model 'Discount'
        db.delete_table('product_discount')
        
        # Deleting model 'DownloadableProduct'
        db.delete_table('product_downloadableproduct')
        
        # Deleting model 'OptionGroup'
        db.delete_table('product_optiongroup')
        
        # Deleting model 'CustomProduct'
        db.delete_table('product_customproduct')
        
        # Deleting model 'Product'
        db.delete_table('product_product')
        
        # Deleting model 'ProductImageTranslation'
        db.delete_table('product_productimagetranslation')
        
        # Deleting model 'OptionGroupTranslation'
        db.delete_table('product_optiongrouptranslation')
        
        # Deleting model 'ProductImage'
        db.delete_table('product_productimage')
        
        # Deleting model 'Option'
        db.delete_table('product_option')
        
        # Deleting model 'SubscriptionProduct'
        db.delete_table('product_subscriptionproduct')
        
        # Deleting model 'ProductTranslation'
        db.delete_table('product_producttranslation')
        
        # Dropping ManyToManyField 'Category.related_categories'
        db.delete_table('product_category_related_categories')
        
        # Dropping ManyToManyField 'ConfigurableProduct.option_group'
        db.delete_table('product_configurableproduct_option_group')
        
        # Dropping ManyToManyField 'ProductVariation.options'
        db.delete_table('product_productvariation_options')
        
        # Dropping ManyToManyField 'CustomProduct.option_group'
        db.delete_table('product_customproduct_option_group')
        
        # Dropping ManyToManyField 'Product.also_purchased'
        db.delete_table('product_product_also_purchased')
        
        # Dropping ManyToManyField 'Discount.validProducts'
        db.delete_table('product_discount_validProducts')
        
        # Dropping ManyToManyField 'Product.related_items'
        db.delete_table('product_product_related_items')
        
        # Dropping ManyToManyField 'Product.category'
        db.delete_table('product_product_category')
        
    
    
    models = {
        'product.category': {
            'Meta': {'unique_together': "(('site', 'slug'),)"},
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'meta': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'ordering': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'child'", 'blank': 'True', 'null': 'True', 'to': "orm['product.Category']"}),
            'related_categories': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['product.Category']", 'null': 'True', 'blank': 'True'}),
            'site': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sites.Site']"}),
            'slug': ('django.db.models.fields.SlugField', [], {'db_index': 'True', 'max_length': '50', 'blank': 'True'})
        },
        'product.categoryimage': {
            'Meta': {'unique_together': "(('category', 'sort'),)"},
            'caption': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'category': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'images'", 'blank': 'True', 'null': 'True', 'to': "orm['product.Category']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'picture': ('ImageWithThumbnailField', [], {'name_field': '"_filename"', 'max_length': '200'}),
            'sort': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        'product.categoryimagetranslation': {
            'Meta': {'unique_together': "(('categoryimage', 'languagecode', 'version'),)"},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'caption': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'categoryimage': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'translations'", 'to': "orm['product.CategoryImage']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'languagecode': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'version': ('django.db.models.fields.IntegerField', [], {'default': '1'})
        },
        'product.categorytranslation': {
            'Meta': {'unique_together': "(('category', 'languagecode', 'version'),)"},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'category': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'translations'", 'to': "orm['product.Category']"}),
            'description': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'languagecode': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'version': ('django.db.models.fields.IntegerField', [], {'default': '1'})
        },
        'product.configurableproduct': {
            'create_subs': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'option_group': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['product.OptionGroup']", 'blank': 'True'}),
            'product': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['product.Product']", 'unique': 'True', 'primary_key': 'True'})
        },
        'product.customproduct': {
            'deferred_shipping': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'downpayment': ('django.db.models.fields.IntegerField', [], {'default': '20'}),
            'option_group': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['product.OptionGroup']", 'blank': 'True'}),
            'product': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['product.Product']", 'unique': 'True', 'primary_key': 'True'})
        },
        'product.customtextfield': {
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'price_change': ('CurrencyField', ['_("Price Change")'], {'null': 'True', 'max_digits': '14', 'decimal_places': '6', 'blank': 'True'}),
            'products': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'custom_text_fields'", 'to': "orm['product.CustomProduct']"}),
            'slug': ('django.db.models.fields.SlugField', [], {'db_index': 'True', 'max_length': '50', 'blank': 'True'}),
            'sort_order': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        'product.customtextfieldtranslation': {
            'Meta': {'unique_together': "(('customtextfield', 'languagecode', 'version'),)"},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'customtextfield': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'translations'", 'to': "orm['product.CustomTextField']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'languagecode': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'version': ('django.db.models.fields.IntegerField', [], {'default': '1'})
        },
        'product.discount': {
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'allValid': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'allowedUses': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'amount': ('CurrencyField', ['_("Discount Amount")'], {'null': 'True', 'max_digits': '8', 'decimal_places': '2', 'blank': 'True'}),
            'automatic': ('django.db.models.fields.NullBooleanField', [], {'default': 'False', 'null': 'True', 'blank': 'True'}),
            'code': ('django.db.models.fields.CharField', [], {'max_length': '20', 'unique': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'endDate': ('django.db.models.fields.DateField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'minOrder': ('CurrencyField', ['_("Minimum order value")'], {'null': 'True', 'max_digits': '8', 'decimal_places': '2', 'blank': 'True'}),
            'numUses': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'percentage': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '5', 'decimal_places': '2', 'blank': 'True'}),
            'shipping': ('django.db.models.fields.CharField', [], {'default': "'NONE'", 'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'site': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sites.Site']"}),
            'startDate': ('django.db.models.fields.DateField', [], {}),
            'validProducts': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['product.Product']", 'null': 'True', 'blank': 'True'})
        },
        'product.downloadableproduct': {
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'expire_minutes': ('django.db.models.fields.IntegerField', [], {}),
            'file': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            'num_allowed_downloads': ('django.db.models.fields.IntegerField', [], {}),
            'product': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['product.Product']", 'unique': 'True', 'primary_key': 'True'})
        },
        'product.option': {
            'Meta': {'unique_together': "(('option_group', 'value'),)"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'option_group': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['product.OptionGroup']"}),
            'price_change': ('CurrencyField', ['_("Price Change")'], {'null': 'True', 'max_digits': '14', 'decimal_places': '6', 'blank': 'True'}),
            'sort_order': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'product.optiongroup': {
            'description': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'site': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sites.Site']"}),
            'sort_order': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        'product.optiongrouptranslation': {
            'Meta': {'unique_together': "(('optiongroup', 'languagecode', 'version'),)"},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'languagecode': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'optiongroup': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'translations'", 'to': "orm['product.OptionGroup']"}),
            'version': ('django.db.models.fields.IntegerField', [], {'default': '1'})
        },
        'product.optiontranslation': {
            'Meta': {'unique_together': "(('option', 'languagecode', 'version'),)"},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'languagecode': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'option': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'translations'", 'to': "orm['product.Option']"}),
            'version': ('django.db.models.fields.IntegerField', [], {'default': '1'})
        },
        'product.price': {
            'Meta': {'unique_together': "(('product', 'quantity', 'expires'),)"},
            'expires': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'price': ('CurrencyField', ['_("Price")'], {'max_digits': '14', 'decimal_places': '6'}),
            'product': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['product.Product']"}),
            'quantity': ('django.db.models.fields.DecimalField', [], {'default': "'1.0'", 'max_digits': '18', 'decimal_places': '6'})
        },
        'product.product': {
            'Meta': {'unique_together': "(('site', 'sku'), ('site', 'slug'))"},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'also_purchased': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['product.Product']", 'null': 'True', 'blank': 'True'}),
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
            'related_items': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['product.Product']", 'null': 'True', 'blank': 'True'}),
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
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'languagecode': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.SlugField', [], {'max_length': '100', 'db_index': 'True'}),
            'product': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['product.Product']"}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'product.productimage': {
            'caption': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'picture': ('ImageWithThumbnailField', [], {'name_field': '"_filename"', 'max_length': '200'}),
            'product': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['product.Product']", 'null': 'True', 'blank': 'True'}),
            'sort': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        'product.productimagetranslation': {
            'Meta': {'unique_together': "(('productimage', 'languagecode', 'version'),)"},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'caption': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'languagecode': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'productimage': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'translations'", 'to': "orm['product.ProductImage']"}),
            'version': ('django.db.models.fields.IntegerField', [], {'default': '1'})
        },
        'product.productpricelookup': {
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
            'Meta': {'unique_together': "(('product', 'languagecode', 'version'),)"},
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
            'options': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['product.Option']"}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['product.ConfigurableProduct']"}),
            'product': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['product.Product']", 'unique': 'True', 'primary_key': 'True'})
        },
        'product.subscriptionproduct': {
            'expire_length': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'expire_unit': ('django.db.models.fields.CharField', [], {'default': "'DAY'", 'max_length': '5'}),
            'is_shippable': ('django.db.models.fields.IntegerField', [], {'max_length': '1'}),
            'product': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['product.Product']", 'unique': 'True', 'primary_key': 'True'}),
            'recurring': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'recurring_times': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        'product.taxclass': {
            'description': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '20'})
        },
        'product.trial': {
            'expire_length': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'price': ('CurrencyField', ['_("Price")'], {'null': 'True', 'max_digits': '10', 'decimal_places': '2'}),
            'subscription': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['product.SubscriptionProduct']"})
        },
        'sites.site': {
            'Meta': {'db_table': "'django_site'"},
            'domain': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        }
    }
    
    complete_apps = ['product']
