#-*- coding:utf-8 -*-
from django.db import models
from django.utils.translation import ugettext_lazy as _

from yt_object.models import YTObject
from technologies.models import Technology
from manufactureplan.models import OperationRecord
from manufactureplan.models import OperationGroupRecord
from manufactureplan.models import ManufacturePlan
from manufactureplan.models import ProductionLine
from manufactureplan.models import RejectProductRecord


#机械加工工艺过程卡
class ReportTechnology(YTObject):
	
    name = models.CharField(max_length=20, verbose_name=_("name"))
    technology = models.ForeignKey(Technology, verbose_name=_("technology"))

    class Meta:
        verbose_name_plural = _('report technology')
        ordering = ("code", )

    def __unicode__(self):
        return "%s" %(self.code)

    @property 
    def pic_code(self):
        return self.code[10:-4]


#产品生产质量控制记录表
class ReportQuality(YTObject):

    name = models.CharField(max_length=20, verbose_name=_("name"))
    #productionline = models.ForeignKey(ProductionLine, verbose_name=_("productionline"))

    class Meta:
        verbose_name_plural = _('report quality')
        ordering = ("code", )

    def __unicode__(self):
        return "%s" %(self.code)

    @property 
    def pic_code(self):
        return self.code[10:-3]

#工序首件三检实测数据记录表
class ReportFirstItem(YTObject):

    name = models.CharField(max_length=20, verbose_name=_("name"))
    productionline = models.ForeignKey(ProductionLine, verbose_name=_("productionline"))

    class Meta:
        verbose_name_plural = _('report record')
        ordering = ("code", )

    def __unicode__(self):
        return "%s" %(self.code)

    @property 
    def pic_code(self):
        return self.code[10:-3]

#质量记录表（不合格处理单）
class ReportReject(YTObject):

    name = models.CharField(max_length=20, verbose_name=_("name"))
    productionline = models.ForeignKey(ProductionLine, verbose_name=_("productionline"))

    class Meta:
        verbose_name_plural = _('report fall')
        ordering = ("code", )

    def __unicode__(self):
        return "%s" %(self.code)

    @property 
    def pic_code(self):
        return self.code[10:-3]

#生产通知单（计划单）
class ReportPlan(YTObject):

    name = models.CharField(max_length=20, verbose_name=_("name"))
    manufactureplan = models.ForeignKey(ManufacturePlan, verbose_name=_("manufactureplan"))

    class Meta:
        verbose_name_plural = _('report plan')
        ordering = ("code", )

    def __unicode__(self):
        return "%s" %(self.code)

    @property 
    def month(self):
        return self.code[10:-4]