#-*- coding:UTF-8 -*-
from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext_lazy as _
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
import os

from managers import *

# Create your models here.


class Category(models.Model):
    name        = models.CharField(_('category name'), max_length=255)
    parent      = models.ForeignKey('self', verbose_name=_('parent category'), null=True, blank=True, related_name='children')
    description = models.TextField(_('category description'),null=True, blank=True)
    photo       = models.ImageField(max_length=255, upload_to="uploads/photos/weboffer/category", blank=True, null=True)
    is_published= models.BooleanField(_('is category published'))
    ext_code    = models.CharField(_('ext_code'), max_length=128, null=True, blank=True)
    custom1     = models.CharField(_('custom1'), max_length=255, null=True, blank=True)
    custom2     = models.CharField(_('custom2'), max_length=255, null=True, blank=True)
    custom3     = models.CharField(_('custom3'), max_length=255, null=True, blank=True)
    custom4     = models.CharField(_('custom4'), max_length=255, null=True, blank=True)

    objects = CategoryManager()

    def __unicode__(self):
        return self.name

    def __str__(self):
        return 'Category <%d>' % self.id

    def __copy__(self):
        copy_fields = ['name', 'parent', 
                'description', 'photo', 'ext_code', 
                'is_published', 'custom1', 'custom2', 
                'custom3', 'custom4']
        return self.__class__(**dict([(f, getattr(self,f))
            for f in copy_fields]))

    class Meta:
        verbose_name = _('Category')
        verbose_name_plural = _('Categorys')


class Attribute(models.Model):
    name        = models.CharField(_('attribute name'), max_length=255)
    unit        = models.CharField(_('unit'), null=True, blank=True, max_length=5)
    ext_code    = models.CharField(_('ext_code'), max_length=128, null=True, blank=True)
    
    def __unicode__(self):
        if self.unit:
            return "%s(%s)" %(self.name, self.unit)
        else:
            return self.name

    class Meta:
        verbose_name = _('Attribute')
        verbose_name_plural = _('Attributes')
        ordering = ('ext_code',)
    
class Group(models.Model): 
    symbol = models.CharField(_('symbol'), max_length=32, unique=True)
    name = models.CharField(_('group name'), max_length=128)

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = _('Group')
        verbose_name_plural = _('Groups')

    
CHOICE_TYPE = (
    (1, _("End Product")),
    (2, _("Semifinished Product")),
)

class Product(models.Model):
    name        = models.CharField(_('product name'), max_length=255)
    cad_code    = models.CharField(_('cad_code'), max_length=128, unique=True)
    norm_code   = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("norm_code"))
    symbol      = models.CharField(_('symbol'), max_length=128)
    category    = models.ForeignKey(Category, verbose_name=_('product category'), related_name='products')
    type        = models.PositiveSmallIntegerField(choices=CHOICE_TYPE, default=1,verbose_name=_("product type"))
    short_desc  = models.TextField(_('short description'),null=True, blank=True)
    long_desc   = models.TextField(_('long description'),null=True, blank=True)
    is_published= models.BooleanField(_('is product published'))
    ext_code    = models.CharField(_('ext_code'), max_length=128, null=True, blank=True)
    custom1     = models.CharField(_('custom1'), max_length=255, null=True, blank=True)
    custom2     = models.CharField(_('custom2'), max_length=255, null=True, blank=True)
    custom3     = models.CharField(_('custom3'), max_length=255, null=True, blank=True)
    custom4     = models.CharField(_('custom4'), max_length=255, null=True, blank=True)
    groups      = models.ManyToManyField(Group, null=True, blank=True, verbose_name=_('product groups'))
    attributes  = models.ManyToManyField(Attribute, through='ProductAttribute', verbose_name=_('product attributes'))
    created_at  = models.DateTimeField(auto_now_add=True, verbose_name=_('created_at'))
    updated_at  = models.DateTimeField(auto_now_add=True, auto_now=True, verbose_name=_('updated_at'))
    
    objects = ProductManager()
    public_objects = PublishedProductsManager()

    def __unicode__(self):
        return "%s" %(self.cad_code if self.cad_code else "")
    
    class Meta:
        verbose_name = _('Product')
        verbose_name_plural = _('Products')

    @property
    def code(self):
        return self.cad_code

    def __copy__(self):
        copy_fields = ['cad_code', 'symbol', 'name', 'short_desc',
            'long_desc', 'ext_code', 'is_published',
            'custom1', 'custom2', 'custom3', 'custom4']
        return self.__class__(**dict([(f, getattr(self,f))
            for f in copy_fields]))

    def photo(self):
        try: 
            return self.photos.all()[0]
        except IndexError:
            return None

    def intro(self):
        return self.short_desc or self.long_desc
    
@receiver(post_save, sender=Product)
def product_post_save(sender, **kwargs):
    from warehouse.models import Item
    self = kwargs['instance']
    content_type = ContentType.objects.get_for_model(self)
    items = Item.objects.filter(content_type_id=content_type.id,object_id=self.id)
    if items:
        items.update(code=self.cad_code)
    else:
        Item.objects.create(code=self.cad_code,content_object=self)

class ProductPhoto(models.Model):
    product     = models.ForeignKey(Product, verbose_name=_('product'), related_name='photos')
    image = models.ImageField(
            max_length=255,
            upload_to=os.path.join('uploads','products')
            )
    display_order = models.PositiveIntegerField(null=False, blank=False, default=0, verbose_name=_('display_order'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('created_at'))
    updated_at = models.DateTimeField(auto_now_add=True, auto_now=True, verbose_name=_('updated_at'))

    def save(self, force_insert=False, force_update=False):
        if not self.display_order:
            self.display_order = self.product.photos.all().count() + 1        
        return super(ProductPhoto, self).save(force_insert, force_update)

    class Meta:
        verbose_name = _('ProductPhoto')
        verbose_name_plural = _('ProductPhotos')

class ProductAttribute(models.Model):
    product         = models.ForeignKey(Product, related_name="product_attributes", verbose_name=_('product'))
    attribute       = models.ForeignKey(Attribute, verbose_name=_('attribute name'), related_name='with_products')
    display_value   = models.CharField(_('display value'),max_length=255)
    absolute_value  = models.DecimalField(_('absolute value'),max_digits=22,decimal_places=3,blank=True,null=True)
    is_published    = models.BooleanField(_('is published'))
    ext_code        = models.CharField(max_length=128, null=True, blank=True)
    difference      = models.DecimalField(_('difference'),default=0,max_digits=22,decimal_places=3,blank=True,null=True)

    objects = ProductAttributeManager()

    class Meta:
        verbose_name = _('ProductAttribute')
        verbose_name_plural = _('ProductAttributes')
