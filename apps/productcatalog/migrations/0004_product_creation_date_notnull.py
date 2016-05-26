
from south.db import db
from django.db import models
from productcatalog.models import *

class Migration:
    
    def forwards(self, orm):
        db.alter_column('productcatalog_product', 'created_at', models.DateTimeField(auto_now=True, auto_now_add=True, null=False))
        db.alter_column('productcatalog_product', 'updated_at', models.DateTimeField(auto_now=True, auto_now_add=False, null=False))
    
    
    def backwards(self, orm):
        db.alter_column('productcatalog_product', 'created_at', models.DateTimeField(auto_now=True, auto_now_add=True, null=True))
        db.alter_column('productcatalog_product', 'updated_at', models.DateTimeField(auto_now=True, auto_now_add=False, null=True))
    
    
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
            'created_at': ('models.DateTimeField', [], {'auto_now_add': 'True'}),
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
            'symbol': ('models.CharField', [], {'max_length': '128', 'blank': 'True'}),
            'updated_at': ('models.DateTimeField', [], {'auto_now_add': 'True', 'auto_now': 'True'})
        }
    }
    
    complete_apps = ['productcatalog']
