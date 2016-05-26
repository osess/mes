#-*- coding: UTF-8 -*- 
from django.db import models
from django.utils.translation import ugettext_lazy as _

class Customer(models.Model):
    code        = models.CharField(max_length=100, verbose_name=_("customer code"))
    name        = models.CharField(max_length=100, verbose_name=_("name"))
    description = models.CharField(max_length=250, blank=True, null=True, verbose_name=_("description"))
    address     = models.CharField(max_length=125, verbose_name=_("address"))
    city        = models.CharField(max_length=50, blank=True, null=True, verbose_name=_("city"))
    state       = models.CharField(max_length=10,blank=True, null=True, verbose_name=_("state"))
    telephone   = models.CharField(max_length=20, blank=True, null=True, verbose_name=_("telephone"))
    mail        = models.EmailField(max_length=50, blank=True, null=True, verbose_name=_("mail"))
    zip_code    = models.CharField(max_length=7, blank=True, null=True, verbose_name=_("zip_code"))
    importance  = models.PositiveSmallIntegerField(default=1, verbose_name=_("importance"))
    
    class Meta:
        verbose_name = _('customer')
        verbose_name_plural = _('customers')
        ordering = ('-name',)

    def __unicode__(self):
        return "%s" %(self.name)


class Contactor(models.Model):
    name        = models.CharField(max_length=125,unique=True, verbose_name=_("contactor name"))
    description = models.CharField(max_length=250, blank=True, verbose_name=_("contactor description"))
    gender      = models.CharField(max_length=100, blank=True, null=True, verbose_name=_("gender"))
    tel         = models.CharField(max_length=50, blank=True, null=True, verbose_name=_("tel"))
    phone       = models.CharField(max_length=50, blank=True, null=True, verbose_name=_("phone"))
    customer    = models.ForeignKey(Customer, related_name="contactors", verbose_name=_("customer"))
    note        = models.CharField(max_length=125, blank=True, null=True, default='' ,verbose_name=_("contactor note"))
    
    class Meta:
        verbose_name = _('contactors')
        verbose_name_plural = _('contactors')
        ordering = ('-name',)
    
    def __unicode__(self):
        return "%s" %(self.name)
