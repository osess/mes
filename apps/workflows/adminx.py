#-*- coding: UTF-8 -*-
import xadmin

from models import *


class WorkflowAdmin(object):
    model_icon = 'cog'
    hidden_menu = False
    list_display = (
        'name', 'initial_state', 'permissions',
       )

    list_filter = ['name', 'initial_state', 'permissions']
    search_fields = ['name']


class StateAdmin(object):
    model_icon = 'cog'
    hidden_menu = False
    list_display = (
        'name', 'workflow', 'transitions',)

    list_filter = ['name', 'workflow', 'transitions']
    search_fields = ['name']


class TransitionAdmin(object):
    model_icon = 'cog'
    hidden_menu = False
    list_display = (
        'name', 'workflow', 'destination', 'condition',
        'permission',
       )

    list_filter = ['name', 'workflow', 'destination', 'condition',
        'permission']
    search_fields = ['name']


class StateObjectRelationAdmin(object):
    model_icon = 'cog'
    hidden_menu = False
    list_display = (
        'state',
       )

    list_filter = ['state']
    search_fields = ['state']


class WorkflowObjectRelationAdmin(object):
    model_icon = 'cog'
    hidden_menu = False
    list_display = (
        'workflow',
       )

    list_filter = ['workflow']
    search_fields = ['workflow']


class WorkflowModelRelationAdmin(object):
    model_icon = 'cog'
    hidden_menu = False
    list_display = (
        'workflow',
       )

    list_filter = ['workflow']
    search_fields = ['workflow']



class WorkflowPermissionRelationAdmin(object):
    model_icon = 'cog'
    hidden_menu = False
    list_display = (
        'workflow', 'permission',
       )

    list_filter = ['workflow', 'permission']
    search_fields = ['workflow']


class StateInheritanceBlockAdmin(object):
    model_icon = 'cog'
    hidden_menu = False
    list_display = (
        'state', 'permission',
       )

    list_filter = ['state', 'permission']
    search_fields = ['state']


class StatePermissionRelationAdmin(object):
    model_icon = 'cog'
    hidden_menu = False
    list_display = (
        'state', 'permission', 'role',
       )

    list_filter = ['state', 'permission', 'role']
    search_fields = ['state']


xadmin.site.register(Workflow, WorkflowAdmin)
xadmin.site.register(State, StateAdmin)
xadmin.site.register(Transition, TransitionAdmin)
xadmin.site.register(StateObjectRelation, StateObjectRelationAdmin)
xadmin.site.register(WorkflowObjectRelation, WorkflowObjectRelationAdmin)
xadmin.site.register(WorkflowModelRelation, WorkflowModelRelationAdmin)
xadmin.site.register(WorkflowPermissionRelation, WorkflowPermissionRelationAdmin)
xadmin.site.register(StateInheritanceBlock, StateInheritanceBlockAdmin)
xadmin.site.register(StatePermissionRelation, StatePermissionRelationAdmin)
