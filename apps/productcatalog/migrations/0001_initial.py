
from south.db import db
from django.db import models
from productcatalog.models import *

class Migration:
    
    def forwards(self, orm):
        
        # Adding model 'Category'
        db.create_table('productcatalog_category', (
            ('description', models.TextField(_('category description'), null=True, blank=True)),
            ('parent', models.ForeignKey(orm.Category, related_name='children', null=True, verbose_name=_('parent category'), blank=True)),
            ('custom4', models.CharField(max_length=255, null=True, blank=True)),
            ('photo', models.ImageField(null=True, max_length=255, blank=True)),
            ('custom1', models.CharField(max_length=255, null=True, blank=True)),
            ('custom2', models.CharField(max_length=255, null=True, blank=True)),
            ('name', models.CharField(_('category name'), max_length=255)),
            ('ext_code', models.CharField(max_length=128, null=True, blank=True)),
            ('custom3', models.CharField(max_length=255, null=True, blank=True)),
            ('id', models.AutoField(primary_key=True)),
            ('is_published', models.BooleanField(_('is category published'))),
        ))
        db.send_create_signal('productcatalog', ['Category'])
        
        # Adding model 'ProductAttribute'
        db.create_table('productcatalog_productattribute', (
            ('product', models.ForeignKey(orm.Product, verbose_name=_('product'))),
            ('attribute', models.ForeignKey(orm.Attribute, related_name='with_products', verbose_name=_('attribute name'))),
            ('display_value', models.CharField(_('display value'), max_length=255)),
            ('ext_code', models.CharField(max_length=128, null=True, blank=True)),
            ('absolute_value', models.DecimalField(_('absolute value'), null=True, max_digits=22, decimal_places=3, blank=True)),
            ('id', models.AutoField(primary_key=True)),
            ('is_published', models.BooleanField(_('is published'))),
        ))
        db.send_create_signal('productcatalog', ['ProductAttribute'])
        
        # Adding model 'Group'
        db.create_table('productcatalog_group', (
            ('symbol', models.CharField(unique=True, max_length=32)),
            ('id', models.AutoField(primary_key=True)),
            ('name', models.CharField(max_length=128)),
        ))
        db.send_create_signal('productcatalog', ['Group'])
        
        # Adding model 'ProductPhoto'
        db.create_table('productcatalog_productphoto', (
            ('product', models.ForeignKey(orm.Product, related_name='photos', verbose_name=_('product'))),
            ('created_at', models.DateTimeField(auto_now_add=True)),
            ('updated_at', models.DateTimeField(auto_now_add=True, auto_now=True)),
            ('id', models.AutoField(primary_key=True)),
            ('image', models.ImageField(max_length=255)),
            ('display_order', models.PositiveIntegerField(default=0, null=False, blank=False)),
        ))
        db.send_create_signal('productcatalog', ['ProductPhoto'])
        
        # Adding model 'Attribute'
        db.create_table('productcatalog_attribute', (
            ('ext_code', models.CharField(max_length=128, null=True, blank=True)),
            ('id', models.AutoField(primary_key=True)),
            ('name', models.CharField(_('attribute name'), max_length=255)),
        ))
        db.send_create_signal('productcatalog', ['Attribute'])
        
        # Adding model 'Product'
        db.create_table('productcatalog_product', (
            ('category', models.ForeignKey(orm.Category, related_name='products', verbose_name=_('category'))),
            ('long_desc', models.TextField(_('long description'), null=True, blank=True)),
            ('name', models.CharField(_('name'), max_length=255)),
            ('custom4', models.CharField(max_length=255, null=True, blank=True)),
            ('symbol', models.CharField(max_length=128, blank=True)),
            ('short_desc', models.TextField(_('short description'), null=True, blank=True)),
            ('custom1', models.CharField(max_length=255, null=True, blank=True)),
            ('custom2', models.CharField(max_length=255, null=True, blank=True)),
            ('custom3', models.CharField(max_length=255, null=True, blank=True)),
            ('ext_code', models.CharField(max_length=128, null=True, blank=True)),
            ('id', models.AutoField(primary_key=True)),
            ('is_published', models.BooleanField(_('is product published'))),
        ))
        db.send_create_signal('productcatalog', ['Product'])
        
        # Adding ManyToManyField 'Product.groups'
        db.create_table('productcatalog_product_groups', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('product', models.ForeignKey(Product, null=False)),
            ('group', models.ForeignKey(Group, null=False))
        ))
        
    
    
    def backwards(self, orm):
        
        # Deleting model 'Category'
        db.delete_table('productcatalog_category')
        
        # Deleting model 'ProductAttribute'
        db.delete_table('productcatalog_productattribute')
        
        # Deleting model 'Group'
        db.delete_table('productcatalog_group')
        
        # Deleting model 'ProductPhoto'
        db.delete_table('productcatalog_productphoto')
        
        # Deleting model 'Attribute'
        db.delete_table('productcatalog_attribute')
        
        # Deleting model 'Product'
        db.delete_table('productcatalog_product')
        
        # Dropping ManyToManyField 'Product.groups'
        db.delete_table('productcatalog_product_groups')
        
    
    
    models = {
        'productcatalog.category': {
            'custom1': ('models.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'custom2': ('models.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'custom3': ('models.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'custom4': ('models.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'description': ('models.TextField', ["_('category description')"], {'null': 'True', 'blank': 'True'}),
            'ext_code': ('models.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'is_published': ('models.BooleanField', ["_('is category published')"], {}),
            'name': ('models.CharField', ["_('category name')"], {'max_length': '255'}),
            'parent': ('models.ForeignKey', ["'self'"], {'related_name': "'children'", 'null': 'True', 'verbose_name': "_('parent category')", 'blank': 'True'}),
            'photo': ('models.ImageField', [], {'null': 'True', 'max_length': '255', 'blank': 'True'})
        },
        'productcatalog.productattribute': {
            'absolute_value': ('models.DecimalField', ["_('absolute value')"], {'null': 'True', 'max_digits': '22', 'decimal_places': '3', 'blank': 'True'}),
            'attribute': ('models.ForeignKey', ['Attribute'], {'related_name': "'with_products'", 'verbose_name': "_('attribute name')"}),
            'display_value': ('models.CharField', ["_('display value')"], {'max_length': '255'}),
            'ext_code': ('models.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'is_published': ('models.BooleanField', ["_('is published')"], {}),
            'product': ('models.ForeignKey', ['Product'], {'verbose_name': "_('product')"})
        },
        'productcatalog.group': {
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'name': ('models.CharField', [], {'max_length': '128'}),
            'symbol': ('models.CharField', [], {'unique': 'True', 'max_length': '32'})
        },
        'productcatalog.productphoto': {
            'created_at': ('models.DateTimeField', [], {'auto_now_add': 'True'}),
            'display_order': ('models.PositiveIntegerField', [], {'default': '0', 'null': 'False', 'blank': 'False'}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'image': ('models.ImageField', [], {'max_length': '255'}),
            'product': ('models.ForeignKey', ['Product'], {'related_name': "'photos'", 'verbose_name': "_('product')"}),
            'updated_at': ('models.DateTimeField', [], {'auto_now_add': 'True', 'auto_now': 'True'})
        },
        'productcatalog.attribute': {
            'ext_code': ('models.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'name': ('models.CharField', ["_('attribute name')"], {'max_length': '255'})
        },
        'productcatalog.product': {
            'attributes': ('models.ManyToManyField', ['Attribute'], {'through': "'ProductAttribute'"}),
            'category': ('models.ForeignKey', ['Category'], {'related_name': "'products'", 'verbose_name': "_('category')"}),
            'custom1': ('models.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'custom2': ('models.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'custom3': ('models.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'custom4': ('models.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'ext_code': ('models.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'groups': ('models.ManyToManyField', ['Group'], {'null': 'True', 'blank': 'True'}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'is_published': ('models.BooleanField', ["_('is product published')"], {}),
            'long_desc': ('models.TextField', ["_('long description')"], {'null': 'True', 'blank': 'True'}),
            'name': ('models.CharField', ["_('name')"], {'max_length': '255'}),
            'short_desc': ('models.TextField', ["_('short description')"], {'null': 'True', 'blank': 'True'}),
            'symbol': ('models.CharField', [], {'max_length': '128', 'blank': 'True'})
        }
    }
    
    complete_apps = ['productcatalog']
