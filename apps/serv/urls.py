from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template


urlpatterns = patterns("",
    url(r'^$', 'serv.views.homepage', name="main"),
    url(r'^create/$', 'serv.views.create', name="main_create"),
)
