from django.conf.urls import patterns, include, url

urlpatterns = patterns('yt_file.views',
    url(r'^fileslist/$', 'files_list', name='fileslist'),
    url(r'^upload/(?P<contenttype_id>\d+)/(?P<object_id>\d+)/$', 'upload_file', name='uploadfile'),
    url(r'^uploadsuccess/(?P<file_id>\d+)/$', 'uploadsuccess', name='uploadsuccess'),
    url(r'^remove/(?P<file_id>\d+)/$', 'file_remove', name='fileremove'),
    url(r'^delete/(?P<file_id>\d+)/$', 'file_delete', name='filedelete'),
    url(r'^show/(?P<file_id>\d+)/$', 'uploadsuccess', name='fileshow'),
    url(r'^download/(?P<file_id>\d+)/$', 'download_directory_file', name='download_directory_file'),
    url(r'^view_files/(?P<contenttype_id>\d+)/(?P<object_id>\d+)/$', 'view_files', name='view_files'),
    # url(r'^download/(?P<file_id>\d+)/$', 'download_directory_files', name='download_directory_files'),
)