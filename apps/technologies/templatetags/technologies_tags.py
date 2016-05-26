#-*- coding: UTF-8 -*- 
from django import template  
from django.contrib.auth.models import User, Group
from django.utils.translation import ugettext_lazy as _
from permissions.models import Permission,PrincipalRoleRelation
from permissions.utils import *
from workflows.models import State,StatePermissionRelation
from workflows.utils import *
from technologies.models import *
from yt_log.models import WorkflowLog, StateDetail
register = template.Library()


@register.simple_tag
def technology_workflow(content_object):
    technology_workflow_content = ''
    workflow = get_workflow(content_object)
    workflow_object_relation = content_object.workflow_object_relation
    current_state = get_state(content_object)
    states = State.objects.filter(workflow=workflow).order_by('id')
    technology_workflow_content = technology_workflow_content+"<table class='table table-bordered'>"
    technology_workflow_content = technology_workflow_content+"<tr>"
    #add executor tr
    executor_content = ''
    executor_content = executor_content + "<tr>"
    for state in states:
        users = []
        permission = Permission.objects.get(codename='check')
        state_permission_relations =StatePermissionRelation.objects.filter(state=state,permission=permission)
        for state_permission_relation in state_permission_relations:
            for group in state_permission_relation.role.get_groups():
                users.extend(group.user_set.all())
            for user in state_permission_relation.role.get_users():
                users.append(user)
        users = list(set(users))

        #set color
        state_detail = StateDetail.objects.get(workflow_object_relation=workflow_object_relation,state=state)
        if state_detail.status == 1:
            technology_workflow_content = technology_workflow_content+"<td>"
        elif state_detail.status == 0:
            technology_workflow_content = technology_workflow_content+"<td bgcolor='#FFFF00'>"
        elif state_detail.status == 2:
            technology_workflow_content = technology_workflow_content+"<td bgcolor='#00FF00'>"
        elif state_detail.status == 3:
            technology_workflow_content = technology_workflow_content+"<td bgcolor='#FF0000'>"

        technology_workflow_content = technology_workflow_content+state.name
        #add user
        if state == current_state:
            for user in users:
                if has_permission(content_object,user,"check"):
                    technology_workflow_content = technology_workflow_content+"<br><span class='label label-info'>"
                    technology_workflow_content = technology_workflow_content+user.last_name+user.first_name+"</span>"
        technology_workflow_content = technology_workflow_content+"</td>"
    '''
        #get Workflow_logs
        workflow_logs = WorkflowLog.objects.filter(state_detail=state_detail).order_by('date_modified')
        executor_content = executor_content + "<td>"
        for workflow_log in workflow_logs:
            tag = ''
            if workflow_log.type == 1:
                tag = ' ->'
            elif workflow_log.type == 2:
                tag = ' <-'
            #add note to this
            executor_content = executor_content + "<a id='" + str(workflow_log.id) + "' class='workflow_log'"
            executor_content = executor_content + " href='javascript:void(0)' hide='" + workflow_log.note + "'"
            executor_content = executor_content + ">" + workflow_log.executor.get_full_name() + '</a>' + tag + '<br>'
        executor_content = executor_content + "</td>"
        
    executor_content = executor_content + "</tr>"
    '''
    #get Workflow_logs
    workflow_logs = WorkflowLog.objects.filter(state_detail__workflow_object_relation=workflow_object_relation).order_by('date_modified')
    for workflow_log in workflow_logs:
        tag = ''
        if workflow_log.type == 1:
            tag = ' ->'
        elif workflow_log.type == 2:
            tag = ' <-'
        #add note to this
        executor_content = executor_content + "<tr>"
        for state in states:
            executor_content = executor_content + "<td>"
            if state == workflow_log.state_detail.state:
                executor_content = executor_content + "<a id='" + str(workflow_log.id) + "' class='workflow_log'"
                executor_content = executor_content + " href='javascript:void(0)' hide='" + workflow_log.note + "'"
                executor_content = executor_content + ">" + workflow_log.executor.last_name + workflow_log.executor.first_name + '</a>' + tag + '<br>'
            executor_content = executor_content + "</td>"
        executor_content = executor_content + "</tr>"

    technology_workflow_content = technology_workflow_content+"</tr>"
    technology_workflow_content = technology_workflow_content+executor_content
    technology_workflow_content = technology_workflow_content+"</table>"
    return technology_workflow_content