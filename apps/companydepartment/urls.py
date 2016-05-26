from django.conf.urls import patterns, include, url
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('companydepartment.views',

    url(r'^comp/$', 'companys_list', name='companyslist'),
    url(r'^comp/add/$', 'company_add', name='companyadd'),
    url(r'^comp/edit/(?P<company_id>\d+)/$', 'company_edit', name='companyedit'),
    url(r'^comp/del/$', 'company_del', name='companydel'),
    url(r'^comp/compsjson/$', 'json_companys_request', name='companysjson'),
    url(r'^comp/structure/$', 'companys_structure', name='companysstructure'),
    url(r'^comp/(?P<company_id>\d+)/files/$', 'compnay_files_list', name='compnayfileslist'),

    url(r'^dep/$', 'departments_list', name='departmentslist'),
    url(r'^dep/add/$', 'department_add', name='departmentadd'),
    url(r'^dep/edit/(?P<department_id>\d+)/$', 'department_edit', name='departmentedit'),
    url(r'^dep/del/$', 'department_del', name='departmentdel'),
    url(r'^dep/deptsjson/(?P<company_id>\d+)/$', 'json_departments_request', name='departmentsjson'),
    url(r'^dep/structure/(?P<company_id>\d+)/$', 'departments_structure', name='departmentsstructure'),
    url(r'^dep/(?P<department_id>\d+)/files/$', 'department_files_list', name='departmentfileslist'),

)