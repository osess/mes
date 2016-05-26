#-*- coding: UTF-8 -*- 
from django.db import models
from django.contrib.contenttypes import generic
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.generic import GenericRelation
from person.models import Job,Employee
from manufactureplan.models import ManufactureRecord
from warehouse.models import ItemJournal
CHOICE_TIMESHEET_TYPE = (
        (1, _("Work")),
        (2, _("Rest")),
        (3, _("Other")),
        )
class Timesheet(models.Model):
    person = models.ForeignKey(Employee, verbose_name=_("person"))
    start = models.DateTimeField(verbose_name=_('start'))
    date = models.DateField(verbose_name=_('date'))
    end = models.DateTimeField(verbose_name=_('end'))
    #TODO:rest
    type = models.PositiveSmallIntegerField(choices=CHOICE_TIMESHEET_TYPE, default=1, verbose_name=_("type"))
    
    content_type = models.ForeignKey(ContentType, blank=True, null=True)
    object_id = models.PositiveIntegerField(blank=True, null=True)
    content_object = generic.GenericForeignKey('content_type', 'object_id')
    
    date_added = models.DateTimeField(verbose_name=_('date added'), auto_now_add=True)
    date_modified = models.DateTimeField(verbose_name=_('date modified'), auto_now=True)
    
    class Meta:
        verbose_name = _('timesheet')
        verbose_name_plural = _('timesheets')
        ordering = ('-start', 'end')
    
    def __unicode__(self):
        return u"%s %s - %s" % (self.person.name, self.start, self.end)

    @property
    def difference_hours(self):
        return self.end - self.start


from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=Timesheet)
def Timesheet_post_save(sender, **kwargs):
    timesheet = kwargs['instance']
    
    manufacture_record_object = timesheet.content_object
    operation_record_object = manufacture_record_object.operation_record

    knife_object = operation_record_object.knife_items.all()
    tool_object = operation_record_object.tool_items.all()

    device_object = operation_record_object.oper_group_record.device_items.all()

    #convert timedate.timedelta to hour
    time_buffer = timesheet.end - timesheet.start
    time = (time_buffer.seconds)/3600

    damage = ItemJournal.objects.get(id=4)
    for knife in knife_object:
        knife.usage_time += time
        # if knife.usage_time > knife.desigen_lifetime:
        if knife.usage_time > 1000:
            knife.journal = damage
        knife.save()

    for device in device_object:
        device.usage_time += time
        # if device.usage_time > device.desigen_lifetime:
        if device.usage_time > 800000:
            device.journal = damage
        device.save()

