from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('workflows.tools.views',
    url(r'^$', 'workflows_list', name='workflowslist'),
    url(r'^add/$', 'workflow_add', name='addworkflow'),
    url(r'^(?P<workflow_id>\d+)/show$', 'workflow_show', name='workflowshow'),
    url(r'^(?P<workflow_id>\d+)/setpermission$', 'workflow_setpermission', name='workflowsetpermission'),
    url(r'^(?P<workflow_id>\d+)/objects$', 'workflow_objects_list', name='workflowobjectslist'),
    url(r'^(?P<workflow_id>\d+)/object/add/$', 'workflow_object_add', name='addworkflowobject'),
    url(r'^(?P<workflow_id>\d+)/object/(?P<object_id>\d+)/$', 'workflow_states_list', name='stateslist'),
)