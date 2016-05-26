#coding: utf-8
from django.conf.urls import patterns, url

urlpatterns = patterns('manufactureplan.views',


    url(r'^productionlines_list/$', 'productionlines_list', name='productionlines_list'),
    url(r'^working_productionlines_list/$', 'working_productionlines_list', name='working_productionlines_list'),
    url(r'^productionline_states_list/(?P<productionline_id>\d+)/$', 'productionline_states_list', name='productionline_states_list'),
    url(r'^create_productionlines/(?P<manufactureplan_id>\d+)/$', 'adminx_create_new_productionline', name='adminx_create_new_productionline'),
    url(r'^(?P<productionline_id>\d+)/apply_materials/$', 'productionline_apply_materials', name='productionline_apply_materials'),
    
    url(r'^(?P<productionline_id>\d+)/apply_devices/$', 'productionline_apply_devices', name='productionline_apply_devices'),
    url(r'^(?P<oper_group_record_id>\d+)/ajax_get_can_applied_devices/$', 'ajax_oper_group_record_get_can_applied_devices', name='ajax_oper_group_record_get_can_applied_devices'),
    url(r'^(?P<oper_group_record_id>\d+)/ajax_set_applied_devices/$', 'ajax_oper_group_record_set_applied_devices', name='ajax_oper_group_record_set_applied_devices'),
    url(r'^(?P<productionline_id>\d+)/ajax_apply_devices/$', 'ajax_productionline_apply_devices', name='ajax_productionline_apply_devices'),
    url(r'^(?P<productionline_id>\d+)/view_devices/$', 'productionline_view_devices', name='productionline_view_devices'),
    # url(r'^(?P<productionline_id>\d+)/apply_knifes/$', 'productionline_apply_knifes', name='productionline_apply_knifes'),
    # url(r'^(?P<productionline_id>\d+)/ajax_apply_knifes/$', 'ajax_productionline_apply_knifes', name='ajax_productionline_apply_knifes'),
    # url(r'^(?P<productionline_id>\d+)/apply_tools/$', 'productionline_apply_tools', name='productionline_apply_tools'),
    # url(r'^(?P<productionline_id>\d+)/ajax_apply_tools/$', 'ajax_productionline_apply_tools', name='ajax_productionline_apply_tools'),
    
    url(r'^(?P<manufactureplan_id>\d+)/send_programs_file/$', 'productionline_send_programs_file', name='productionline_send_programs_file'),
    
    
    url(r'^operation_working_device_items_list$', 'operation_working_device_items_list', name='operation_working_device_items_list'),
    url(r'^operation_working_start/(?P<device_item_id>\d+)/$', 'operation_working_start', name='operation_working_start'),
    url(r'^operation_working_timing/(?P<device_entry_id>\d+)/(?P<manufacture_item_id>\d+)/$', 'operation_working_timing', name='operation_working_timing'),

    url(r'^manufactureplan_start_workflow/(?P<manufactureplan_id>\d+)/$', 'manufactureplan_start_workflow', name='manufactureplan_start_workflow'),
    url(r'^manufactureplan_workflow/(?P<manufactureplan_id>\d+)/$', 'manufactureplan_workflow', name='manufactureplan_workflow'),
    
    #ajax
    url(r'^item_working_work/$', 'item_working_work', name='item_working_work'),
    url(r'^item_working_rest/$', 'item_working_rest', name='item_working_rest'),
    url(r'^item_working_relation_start/$', 'item_working_relation_start', name='item_working_relation_start'),
    url(r'^item_working_relation_handle/$', 'item_working_relation_handle', name='item_working_relation_handle'),
    url(r'^item_working_finish/$', 'item_working_finish', name='item_working_finish'),
    
    url(r'^ajax_create_bom_entries/(?P<productionline_id>\d+)/$', 'ajax_create_bom_entries', name='ajax_create_bom_entries'),
    
    url(r'^start_workflow/$', 'ajax_productionline_start_workflow', name='ajax_productionline_start_workflow'),

    url(r'^productionlines_monitoring/$', 'productionlines_monitoring', name='productionlines_monitoring'),
    
    url(r'^ajax_get_qa_record_attributes_modal_content/$', 'ajax_get_qa_record_attributes_modal_content', name='ajax_get_qa_record_attributes_modal_content'),
    url(r'^ajax_productionline_auto_apply_devices/$', 'ajax_productionline_auto_apply_devices', name='ajax_productionline_auto_apply_devices'),
    
    url(r'^ajax_import_manufacture_items/$', 'ajax_import_manufacture_items', name='ajax_import_manufacture_items'),
    url(r'^ajax_export_manufacture_items/$', 'ajax_export_manufacture_items', name='ajax_export_manufacture_items'),
    
    url(r'^ajax_update_mig_column/(?P<mig_id>\d+)/$', 'ajax_update_mig_column', name='ajax_update_mig_column'),
    
    # 检验， 去毛刺，热处理，装箱，时效
    url(r'^operation_working_check/$', 'operation_working_check', name='operation_working_check'),
    url(r'^operation_working_wipe_burr/$', 'operation_working_wipe_burr', name='operation_working_wipe_burr'),
    url(r'^operation_working_heattreatment/$', 'operation_working_heattreatment', name='operation_working_heattreatment'),
    url(r'^operation_working_incasement/$', 'operation_working_incasement', name='operation_working_incasement'),
    url(r'^operation_working_period/$', 'operation_working_period', name='operation_working_period'),
    url(r'^operation_working_other/$', 'operation_working_other', name='operation_working_other'),

    # 批量处理
    url(r'^batch_handle/(?P<productionline_id>\d+)/$', 'batch_handle', name='batch_handle'),
    url(r'^handle_batch_check/$', 'handle_batch_check', name='handle_batch_check'),
    url(r'^handle_batch_work_finished/$', 'handle_batch_work_finished', name='handle_batch_work_finished'),

    # 新的处理流程
    url(r'^handle_new_flow_check_qa_record/$', 'handle_new_flow_check_qa_record', name='handle_new_flow_check_qa_record'),
    url(r'^handle_operation_finish/$', 'handle_operation_finish', name='handle_operation_finish'),
    url(r'^handle_qualified/$', 'handle_qualified', name='handle_qualified'),
    url(r'^show_new_qa_modal/(?P<mi_id>\d+)/$', 'show_new_qa_modal', name='show_new_qa_modal'),
)