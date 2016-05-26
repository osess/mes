from django.conf.urls.defaults import *

urlpatterns = patterns('timesheet.views',
	url(r'^(?P<username>[-\w]+)/(?P<year>\d{4})/(?P<week>\d{2})/$',
		view = 'week_archive',
		name = 'timesheet_week_archive',
	),
)