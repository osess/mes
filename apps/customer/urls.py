from django.conf.urls import patterns, include, url
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('customer.views',
    '''
    url(r'^list/$', 'customers_list', name='customers_list'),
    url(r'^add/$', 'customer_add', name='customer_add'),
    url(r'^edit/(?P<customer_id>\d+)/$', 'customer_edit', name='customer_edit'),
    url(r'^del/$', 'customer_del', name='customer_del'),
    '''
)