#－*－ coding:utf-8 -*-
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from customer.models import Customer
#from warehouse.models import Location
from yt_object.models import YTObject
from productcatalog.models import Product


class Material(YTObject):

    #牌号，标准代号，硬度，种类，剖面尺寸，长度，但件质量kg
    #小问题，先不写成attribute
    name     = models.CharField(max_length=125, unique=False, verbose_name=_("material name"))
    
    product         = models.ForeignKey(Product, related_name='material', blank=True, null=True, verbose_name=_('product'))
    owner    = models.ForeignKey(Customer, related_name='material', blank=True, null=True, verbose_name=_("material owner"))
    furnace_batch   = models.CharField(max_length=125, blank=True, null=True, verbose_name=_("material furnace_batch"))
    mark            = models.CharField(max_length=125, blank=True, null=True, verbose_name=_("material mark"))
    norm            = models.CharField(max_length=125, blank=True, null=True, verbose_name=_("material norm"))

    category = models.CharField(max_length=125, unique=False, blank=True, null=True, verbose_name=_("material category"))
    hardness = models.CharField(max_length=125, unique=False, blank=True, null=True, verbose_name=_("hardness"))
    length   = models.CharField(max_length=125, unique=False, blank=True, null=True, verbose_name=_("length"))
    weight   = models.CharField(max_length=125, unique=False, blank=True, null=True, verbose_name=_("weight"))
    

    def __unicode__(self):
        return "%s:%s" %(self.name, self.code)

    class Meta:
        verbose_name_plural = _('Materials')
        ordering = ('id',)

@receiver(post_save, sender=Material)
def material_post_save(sender, **kwargs):
    from warehouse.models import Item
    self = kwargs['instance']
    content_type = ContentType.objects.get_for_model(self)
    items = Item.objects.filter(content_type_id=content_type.id,object_id=self.id)
    if items:
        items.update(code=self.mark)
    else:
        Item.objects.create(code=self.mark,content_object=self)

class Workblank(Material):

    class Meta:
        verbose_name_plural = _('Workblanks')
        ordering = ('id',)

Workblank._meta.get_field('name').verbose_name = _("workblank name")
Workblank._meta.get_field('category').verbose_name = _("workblank category")
    
