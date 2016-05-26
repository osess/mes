# -*- coding: utf8 -*-

from django.db import models
from mptt.models import MPTTModel,TreeForeignKey
from django.utils.translation import get_language_from_request, ugettext_lazy as _

#import hr.models


class Company(MPTTModel):
    name = models.CharField(max_length=125,unique=True, verbose_name=_("name"))
    #parent_company = models.ForeignKey('self', blank=True, null=True, related_name="children")
    parent = TreeForeignKey('self', blank=True, null=True, related_name="children", verbose_name=_("parent company"))
    description = models.CharField(max_length=250, blank=True, verbose_name=_("description"))
    address = models.CharField(max_length=125, blank=True, null=True, verbose_name=_("address"))
    city = models.CharField(max_length=50, blank=True, null=True, verbose_name=_("city"))
    state = models.CharField(max_length=10,blank=True, null=True, verbose_name=_("state"))
    zip_code = models.CharField(max_length=7, blank=True, null=True, verbose_name=_("zip code"))
    importance = models.PositiveSmallIntegerField(default=99, verbose_name=_("importance"))
    latitude = models.FloatField(blank=True, null=True, verbose_name=_("latitude"))
    longitude = models.FloatField(blank=True, null=True,verbose_name=_("longitude"))
    date_added = models.DateTimeField(auto_now_add=True, verbose_name=_("date added"))
    date_modified = models.DateTimeField(auto_now=True, verbose_name=_("date modified"))

    class Meta:
        verbose_name = 'company'
        verbose_name_plural = 'companies'
        ordering = ('-name',)

    def __unicode__(self):
        return "%s" %(self.name)

class Department(MPTTModel):
    dpid = models.CharField(max_length=10, blank=True, null=True, verbose_name=_("id"))#TODO unique=True)
    name = models.CharField(max_length=125,verbose_name=_("name"))
    #director = models.ForeignKey(Account, verbose_name=_("director"))
    belong_to = models.ForeignKey(Company, related_name="departments", verbose_name=_("company belongs to"))
    #parent_department = models.ForeignKey('self', blank=True, null=True, related_name="children")
    parent = TreeForeignKey('self', blank=True, null=True, related_name="children", verbose_name=_("parent department"))
    description = models.CharField(max_length=250, blank=True, verbose_name=_("description"))
    telephone = models.CharField(max_length=20, blank=True, null=True, verbose_name=_("telephone"))
    address = models.CharField(max_length=125, blank=True, null=True, verbose_name=_("address"))
    city = models.CharField(max_length=50, blank=True, null=True, verbose_name=_("city"))
    state = models.CharField(max_length=10,blank=True, null=True, verbose_name=_("state"))
    zip_code = models.CharField(max_length=7, blank=True, null=True, verbose_name=_("zip code"))
    importance = models.PositiveSmallIntegerField(default=99, verbose_name=_("importance"))
    latitude = models.FloatField(blank=True, null=True, verbose_name=_("latitude"))
    longitude = models.FloatField(blank=True, null=True,verbose_name=_("longitude"))
    date_added = models.DateTimeField(auto_now_add=True, verbose_name=_("date added"))
    date_modified = models.DateTimeField(auto_now=True, verbose_name=_("date modified"))


    class Meta:
        verbose_name = 'department'
        verbose_name_plural = 'departments'
        ordering = ('name', 'importance')

    def __unicode__(self):
        return "%s(%d)" %(self.name, self.importance)

    @property
    def employees_count(self):
        return hr.models.Person.objects.filter(status__lte=10, job__department=self).count()