
from django.conf.urls.defaults import *

urlpatterns = patterns('warehouse.views',
     url(r'^$', 'index', name='warehouse_index'),
     
     url(r'^item/$', 'item_list', name='warehouse_item_index'),
     url(r'^item/(?P<item_code>\w+)/$', 'item_detail', name='warehouse_item_detail'),
)

urlpatterns = urlpatterns + patterns('warehouse.yt_views',
    url(r'^bom_list/$', 'bom_list', name='bom_list'),
    url(r'^bom_detail/(?P<productionline_id>\d+)/$', 'bom_detail', name='bom_detail'),
    url(r'^bom_output/(?P<productionline_id>\d+)/$', 'bom_output', name='bom_output'),
    # url(r'^import_detail/(?P<productionline_id>\d+)/$', 'import_detail', name='import_detail'),
    #url(r'^bom_import/(?P<productionline_id>\d+)/$', 'bom_import', name='bom_import'),
    url(r'^export_list/$', 'export_list', name='export_list'),
    url(r'^export_detail/(?P<export_list_id>\d+)/$', 'export_detail', name='export_detail'),
    url(r'^export_to_warehouse/(?P<export_list_id>\d+)/$', 'export_to_warehouse', name='export_to_warehouse'),

    url(r'^import_list/$', 'import_list', name='import_list'),
    url(r'^import_detail/(?P<import_list_id>\d+)/$', 'import_detail', name='import_detail'),
    url(r'^import_to_warehouse/(?P<import_list_id>\d+)/$', 'import_to_warehouse', name='import_to_warehouse'),
    
    #by xxd
    url(r'^apply_item_entries/$', 'ajax_productionline_apply_item_entries', name='ajax_productionline_apply_item_entries'),
    url(r'^ajax_auto_apply_item_entries/$', 'ajax_auto_apply_item_entries', name='ajax_auto_apply_item_entries'),

    url(r'^applications_list/$', 'applications_list', name='applications_list'),
    url(r'^ajax_set_manu_item_group_item_entries_ready/$', 'ajax_set_manu_item_group_item_entries_ready', name='ajax_set_manu_item_group_item_entries_ready'),
    
    # url(r'^transportlists_list/$', 'transportlists_list', name='transportlists_list'),
    url(r'^transportlists_list/(?P<list_category_number>\d+)/(?P<transport_category>\d+)/$', 'transportlists_list', name='transportlists_list'),

    url(r'^ajax_create_transportlist_verification/$', 'ajax_create_transportlist_verification', name='ajax_create_transportlist_verification'),
    url(r'^create_transportlist/(?P<list_category>\d+)/(?P<transport_category>\d+)/$', 'create_transportlist', name='create_transportlist'),
    url(r'^ajax_do_transport_verification/$', 'ajax_do_transport_verification', name='ajax_do_transport_verification'),
    url(r'^ajax_do_transport/$', 'ajax_do_transport', name='ajax_do_transport'),
    url(r'^transfer_and_verify/$', 'transfer_and_verify', name='transfer_and_verify'),
    #by lxy
    url(r'^ajax_knife_attribute_data/$', 'ajax_knife_attribute_data', name='ajax_knife_attribute_data'),
    url(r'^ajax_chained_selected_modal/$', 'ajax_chained_selected_modal', name='ajax_chained_selected_modal'),
    url(r'^ajax_load_global_data/$', 'ajax_load_global_data', name='ajax_load_global_data'),
    url(r'^ajax_get_notice_data/$', 'ajax_get_notice_data', name='ajax_get_notice_data'),
    
)
