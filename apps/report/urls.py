from django.conf.urls.defaults import *

urlpatterns = patterns('report.views',
    url(r'^first_item/(?P<productionline_id>\w+)/$', 'generate_first_item_report', name='generate_first_item_report'),
    url(r'^technology/(?P<technology_id>\w+)/$', 'generate_technology_report', name='generate_technology_report'),
    url(r'^technology_subpicture/(?P<operation_group_id>\w+)/$', 'generate_technology_subpicture', name='generate_technology_subpicture'),
    url(r'^plan/(?P<manufactureplan_id>\w+)/$', 'generate_plan_report', name='generate_plan_report'),
    url(r'^quality/(?P<productionline_id>\w+)/$', 'generate_quality_report', name='generate_quality_report'),
    url(r'^reject/(?P<productionline_id>\w+)/$', 'generate_reject_project_report', name='generate_reject_project_report'),
    url(r'^single_reject/(?P<manufacture_item_id>\w+)/$', 'generate_single_reject_project_report', name='generate_single_reject_project_report'),
    
    url(r'^item_time/$', 'ext_manufactureitem_working_time', name='ext_manufactureitem_working_time'),
    url(r'^json_item_time/$', 'json_ext_manufactureitem_working_time', name='json_ext_manufactureitem_working_time'),
    url(r'^item_time_detail/(?P<mig_id>\w+)/$', 'ext_manufactureitem_working_time_detail', name='ext_manufactureitem_working_time_detail'),
    url(r'^json_item_time_detail/(?P<mig_id>\w+)/$', 'json_ext_manufactureitem_working_time_detail', name='json_ext_manufactureitem_working_time_detail'),
    url(r'^employee_worked/$', 'ext_employee_worked_manufactureitem', name='ext_employee_worked_manufactureitem'),
    url(r'^json_employee_worked/(?P<year>\w+)/year/$', 'json_ext_employee_worked_manufactureitem', name='json_ext_employee_worked_manufactureitem'),
    url(r'^employee_worked_detail/(?P<employee_id>\w+)/$', 'ext_employee_worked_detail', name='ext_employee_worked_detail'),
    url(r'^json_employee_worked_detail/(?P<employee_id>\w+)/$', 'json_ext_employee_worked_detail', name='json_ext_employee_worked_detail'),
    url(r'^device_time/$', 'ext_device_working_time', name='ext_device_working_time'),
    url(r'^json_device_time/(?P<year>\w+)/year/$', 'json_ext_device_working_time', name='json_ext_device_working_time'),
    url(r'^device_time_detail/(?P<device_entry_id>\w+)/$', 'ext_device_working_time_detail', name='ext_device_working_time_detail'),
    url(r'^json_device_time_detail/(?P<device_entry_id>\w+)/$', 'json_ext_device_working_time_detail', name='json_ext_device_working_time_detail'),
    url(r'^warehouse_inventory/$', 'ext_warehouse_inventory', name='ext_warehouse_inventory'),
    url(r'^json_warehouse_inventory/(?P<year>\w+)/year/$', 'json_ext_warehouse_inventory', name='json_ext_warehouse_inventory'),
    url(r'^warehouse_inventory_detail/(?P<item_id>\w+)/$', 'ext_warehouse_inventory_detail', name='ext_warehouse_inventory_detail'),
    url(r'^json_warehouse_inventory_detail/(?P<item_id>\w+)/$', 'json_ext_warehouse_inventory_detail', name='json_ext_warehouse_inventory_detail'),
    url(r'^knife_scraped/$', 'ext_knife_scraped', name='ext_knife_scraped'),
    url(r'^json_knife_scraped/(?P<year>\w+)/year/$', 'json_ext_knife_scraped', name='json_ext_knife_scraped'),
    url(r'^knife_scraped_detail/(?P<item_id>\w+)/$', 'ext_knife_scraped_detail', name='ext_knife_scraped_detail'),
    url(r'^json_knife_scraped_detail/(?P<item_id>\w+)/$', 'json_ext_knife_scraped_detail', name='json_ext_knife_scraped_detail'),
    
)


