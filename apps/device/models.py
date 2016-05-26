# coding=utf-8
from django.db import models
from django.utils.translation import ugettext_lazy as _
from productcatalog.models import Attribute
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.generic import GenericRelation
from django.contrib.contenttypes import generic
from django.contrib.auth.models import User
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver


class Device(models.Model):

    prefix              = models.CharField(max_length=25, verbose_name=_("device prefix"))
    name                = models.CharField(max_length=255, verbose_name=_("device name"))
    type                = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("device type"))
    producter           = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("producter"))
    desigen_lifetime    = models.IntegerField(max_length=255, blank=True, null=True, verbose_name=_("desigen_lifetime"))
    
    description         = models.CharField(_('device description'), max_length=100, blank=True, null=True)
    
    def __unicode__(self):
        return "%s:%s" %(self.name, self.type)

    class Meta:
        unique_together = ('name', 'type', 'producter')
        verbose_name = _('Device')
        verbose_name_plural = _('Devices')
        ordering = ('id',)

    @property
    def code(self):
        return self.prefix

@receiver(post_save, sender=Device)
def device_post_save(sender, **kwargs):
    from warehouse.models import Item
    self = kwargs['instance']
    content_type = ContentType.objects.get_for_model(self)
    items = Item.objects.filter(content_type_id=content_type.id,object_id=self.id)
    if items:
        items.update(code=self.prefix)
    else:
        Item.objects.create(code=self.prefix,content_object=self)

class Knife(models.Model):
    # 材质 直径 R角度 总长 刃长 刃数 规格
    name             = models.CharField(max_length=255, verbose_name=_("knife name"))
    prefix           = models.CharField(max_length=25, verbose_name=_("knifeprefix"))
    attributes       = models.ManyToManyField(Attribute, blank=True, null=True, through='KnifeAttribute', verbose_name=_("attributes"))
    desigen_lifetime = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("desigen_lifetime"))
    origin_place     = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("origin place"))
    
    def __unicode__(self):
        attribute_values = self.prefix + ':'
        for attribute_value in self.knife_attributes.all():
            if attribute_value.attribute_code:
                attribute_values += str(attribute_value.attribute_code)
                attribute_values += ' - '
        if attribute_values.endswith(" - "):
            attribute_values = attribute_values[0:-3]
        return "%s-%s" %(self.name, self.attributes_values)

    class Meta:
        verbose_name = _('Knife')
        verbose_name_plural = _('Knifes')
        ordering = ('id',)

    @property
    def code(self):
        return self.prefix

    @property
    def attributes_values(self):
        attribute_values = ''
        for attribute_value in self.knife_attributes.all():
            attribute_values = attribute_values + attribute_value.attribute.name
            attribute_values = attribute_values + ':'
            attribute_values = attribute_values + attribute_value.value
            # attribute_values = attribute_values + attribute_value.attribute.unit
            attribute_values = attribute_values + ' | '
        if attribute_values.endswith(" | "):
            attribute_values = attribute_values[0:-3]
        return attribute_values

@receiver(post_save, sender=Knife)
def knife_post_save(sender, **kwargs):
    from warehouse.models import Item
    self = kwargs['instance']
    content_type = ContentType.objects.get_for_model(self)
    items = Item.objects.filter(content_type_id=content_type.id,object_id=self.id)
    if items:
        items.update(code=self.prefix)
    else:
        Item.objects.create(code=self.prefix,content_object=self)


class KnifeAttribute(models.Model):

    knife          = models.ForeignKey(Knife, related_name='knife_attributes', verbose_name=_('knife'))
    attribute      = models.ForeignKey(Attribute, related_name='knife_attributes', verbose_name=_('attribute'))
    value          = models.CharField(max_length=255, verbose_name=_("value"))
    attribute_code = models.IntegerField(max_length=255, blank=True, null=True, verbose_name=_("attribute_code"))

    def __unicode__(self):

        return "%s(%s)" %(self.value, self.attribute.unit)

    class Meta:
        verbose_name = _('KnifeAttribute')
        verbose_name_plural = _('KnifeAttributes')
        ordering = ('knife','attribute')
        unique_together = ('knife', 'attribute',)

CHOICE_TOOL_TYPE = (
    (1, _("General")),
    (2, _("SurveyTool")),
)

class Tool(models.Model):

    prefix    = models.CharField(max_length=25, verbose_name=_("tool prefix"))
    name      = models.CharField(max_length=255, verbose_name=_("tool name"))
    norm      = models.CharField(max_length=255, default="", blank=True, null=True, verbose_name=_("norm"))
    producter = models.CharField(max_length=255, default="", blank=True, null=True, verbose_name=_("producter"))
    type      = models.PositiveSmallIntegerField(choices=CHOICE_TOOL_TYPE, default=1, verbose_name=_("tool type"))

    def __unicode__(self):

        return "%s" %(self.name)

    class Meta:
        verbose_name = _('Tool')
        verbose_name_plural = _('Tools')
        unique_together = ('name', 'norm', 'producter')
        ordering = ('id',)

    @property
    def code(self):
        return self.prefix

@receiver(post_save, sender=Tool)
def tool_post_save(sender, **kwargs):
    from warehouse.models import Item
    self = kwargs['instance']
    content_type = ContentType.objects.get_for_model(self)
    items = Item.objects.filter(content_type_id=content_type.id,object_id=self.id)
    if items:
        items.update(code=self.prefix)
    else:
        Item.objects.create(code=self.prefix,content_object=self)
