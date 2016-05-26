from django.conf.urls import patterns, include, url
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('device.views',

    url(r'^add_knife/$', 'add_knife', name='add_knife'),
    url(r'^db/$', 'db', name='db'),
    

)