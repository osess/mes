from django.conf.urls import patterns, include, url
#from django.contrib import admin
#admin.autodiscover()

urlpatterns = patterns('quality.views',

    url(r'^excessive_qa_records_list/$', 'excessive_qa_records_list', name='excessive_qa_records_list'),
    url(r'^wait_excessive_qa_records_list/$', 'wait_excessive_qa_records_list', name='wait_excessive_qa_records_list'),
    url(r'^pass_excessive_qa_records_list/$', 'pass_excessive_qa_records_list', name='pass_excessive_qa_records_list'),
    url(r'^fail_excessive_qa_records_list/$', 'fail_excessive_qa_records_list', name='fail_excessive_qa_records_list'),
    url(r'^excessive_qa_record_view/(?P<qa_record_id>\d+)/$', 'excessive_qa_record_view', name='excessive_qa_record_view'),
    
    # show all manufacture item with qa record
    url(r'^qa_record_list/$', 'qa_record_list', name='qa_record_list'),
    # show all no_passed manufacture item
    url(r'^blank_no_passed_list/$', 'blank_no_passed_list', name='blank_no_passed_list'),

    url(r'^ajax_qa_record_attribute_decision/$', 'ajax_qa_record_attribute_decision', name='ajax_qa_record_attribute_decision'),
    url(r'^ajax_excessive_qa_record_fail/$', 'ajax_excessive_qa_record_fail', name='ajax_excessive_qa_record_fail'),
    url(r'^ajax_excessive_qa_record_pass/$', 'ajax_excessive_qa_record_pass', name='ajax_excessive_qa_record_pass'),
    url(r'^ajax_decision_fail_qa_record/$', 'ajax_decision_fail_qa_record', name='ajax_decision_fail_qa_record'),
    
)