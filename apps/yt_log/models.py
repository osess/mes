#-*- coding: UTF-8 -*- 
from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from workflows.models import State, Transition, WorkflowObjectRelation
import logging

LOG_LEVELS = (
    (logging.INFO, _('info')),
    (logging.WARNING, _('warning')),
    (logging.DEBUG, _('debug')),
    (logging.ERROR, _('error')),
    (logging.FATAL, _('fatal')),
)

CHOICE_STATE_STATUS = (
    (0, _('Current')),
    (1, _('Waiting')),
    (2, _('Approved')),
    (3, _('Rejected')),
)

CHOICE_TRANSITION_STYPE = (
    (1, _('Approved')),
    (2, _('Rejected')),
)

class StateDetail(models.Model):
    workflow_object_relation = models.ForeignKey(WorkflowObjectRelation, related_name='state_details', verbose_name=_("workflow_object_relation"))
    state = models.ForeignKey(State, related_name='state_details', verbose_name=_("state"))
    status= models.PositiveIntegerField(choices=CHOICE_STATE_STATUS, default=1, verbose_name=_("status"))

    def __unicode__(self):
        return str(self.workflow_object_relation)

class WorkflowLog(models.Model):
    state_detail    = models.ForeignKey(StateDetail, related_name='workflow_logs', verbose_name=_("state_detail"))
    executor        = models.ForeignKey(User, related_name='created_logs', verbose_name=_("user"))
    level           = models.PositiveIntegerField(choices=LOG_LEVELS, default=logging.ERROR, blank=True, db_index=True, verbose_name=_("level"))
    type            = models.PositiveIntegerField(choices=CHOICE_TRANSITION_STYPE, default=2, db_index=True, verbose_name=_("type"))
    note            = models.TextField(null=True, blank=True, verbose_name=_("note"))
    
    date_added      = models.DateTimeField(auto_now_add=True, verbose_name=_("date_added"))
    date_modified   = models.DateTimeField(auto_now=True, verbose_name=_("date_modified"))

    class Meta:
        verbose_name = _('note')
        verbose_name_plural = _('notes')

    def __unicode__(self):
        return "%s" % (self.note,)
