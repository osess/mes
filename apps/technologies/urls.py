#coding:utf-8
from django.conf.urls import patterns, include, url

urlpatterns = patterns('technologies.views',
    
    url(r'^technologies_list/$', 'technologies_list', name='technologies_list'),
    url(r'^(?P<technology_id>\d+)/states_list/$', 'technology_states_list', name='technology_states_list'),
    url(r'^(?P<technology_id>\d+)/workflow/$', 'technology_workflow', name='technology_workflow'),
    url(r'^(?P<technology_id>\d+)/start_workflow/$', 'technology_start_workflow', name='technology_start_workflow'),
    url(r'^(?P<content_type_id>\d+)/(?P<object_id>\d+)/workflow/approve/$', 'ajax_technology_workflow_approve', name='ajax_technology_workflow_approve'),
    url(r'^(?P<content_type_id>\d+)/(?P<object_id>\d+)/workflow/refusal/$', 'ajax_technology_workflow_refusal', name='ajax_technology_workflow_refusal'),
    
    url(r'^technology_excel_import/$', 'technology_excel_import', name='technology_excel_import'),
    url(r'^create/technology/$', 'create_technology', name='create_technology'),
    url(r'^view/technology/(?P<technology_id>\d+)/$', 'view_technology', name='view_technology'),
    url(r'^edit/technology/(?P<technology_id>\d+)/$', 'edit_technology', name='edit_technology'),
    url(r'^create/operation_group/(?P<operation_group_id>\d+)/$', 'create_operation_group', name='create_operation_group'),
    url(r'^view/operation_group/(?P<operation_group_id>\d+)/$', 'view_operation_group', name='view_operation_group'),
    url(r'^edit/operation_group/(?P<operation_group_id>\d+)/$', 'edit_operation_group', name='edit_operation_group'),
    
    url(r'^technology/(?P<technology_id>\d+)/files/$', 'technology_files_list', name='technology_files_list'),
    url(r'^operation_group/(?P<operation_group_id>\d+)/files/$', 'operation_group_files_list', name='operation_group_files_list'),
    
    #ajax
    url(r'^ajax_init_workflow/$', 'ajax_init_workflow', name='ajax_init_workflow'),
    url(r'^ajax_start_object_workflow/$', 'ajax_start_object_workflow', name='ajax_start_object_workflow'),
    url(r'^ajax_technology_update_reversion/(?P<technology_id>\d+)/$', 'ajax_technology_update_reversion', name='ajax_technology_update_reversion'),
    url(r'^ajax_create_technology_verification/$', 'ajax_create_technology_verification', name='ajax_create_technology_verification'),
    url(r'^ajax_create_technology/$', 'ajax_create_technology', name='ajax_create_technology'),
    url(r'^ajax_edit_technology_verification/$', 'ajax_edit_technology_verification', name='ajax_edit_technology_verification'),
    url(r'^ajax_edit_technology/(?P<technology_id>\d+)/$', 'ajax_edit_technology', name='ajax_edit_technology'),
    url(r'^ajax_create_operation_group_verification/$', 'ajax_create_operation_group_verification', name='ajax_create_operation_group_verification'),
    url(r'^ajax_create_operation_group/(?P<operation_group_id>\d+)/$', 'ajax_create_operation_group', name='ajax_create_operation_group'),
    url(r'^ajax_edit_operation_group_verification/$', 'ajax_edit_operation_group_verification', name='ajax_edit_operation_group_verification'),
    url(r'^ajax_edit_operation_group/(?P<operation_group_id>\d+)/$', 'ajax_edit_operation_group', name='ajax_edit_operation_group'),
    

    # 查看需要添加属性的所有工步
    url(r'^view_operation_attribute_needs/(?P<technology_id>\d+)/$', 'view_operation_attribute_needs', name='view_operation_attribute_needs'),
)

urlpatterns += patterns('technologies.views_ajax',
    url(r'^ajax_delete_technology_file/$', 'ajax_delete_technology_file', name='ajax_delete_technology_file'),
    url(r'^ajax_set_operation_not_required/$', 'ajax_set_operation_not_required', name='ajax_set_operation_not_required'),
)