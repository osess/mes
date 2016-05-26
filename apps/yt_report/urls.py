from django.conf.urls import patterns, include, url
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('yt_report.views',
    
    url(r'^$', 'report_management', name='reportmanagement'),
    url(r'^personlisttable/$', 'report_person_list_table', name='personlisttable'),
    url(r'^generate_technology_pdf/(?P<technology_id>\w+)/$', 'generate_technology_pdf', name='generate_technology_pdf'),
    url(r'^generate_technology_subpicture_pdf/(?P<operation_group_id>\w+)/$', 'generate_technology_subpicture_pdf', name='generate_technology_subpicture_pdf'),
    url(r'^generate_first_item_pdf/(?P<productionline_id>\w+)/$', 'generate_first_item_pdf', name='generate_first_item_pdf'),
    url(r'^generate_reject_project_pdf/(?P<productionline_id>\w+)/$', 'generate_reject_project_pdf', name='generate_reject_project_pdf'),    
    url(r'^generate_quality_pdf/(?P<productionline_id>\w+)/$', 'generate_quality_pdf', name='generate_quality_pdf'),    
    url(r'^merge_pdf/(?P<technology_id>\w+)/$', 'merge_pdf', name='merge_pdf'),    

)


