import datetime, time

from django.http import Http404
from django.db.models import Sum
from django.template import RequestContext
from django.contrib.auth.models import User
from django.shortcuts import render_to_response

from timesheet.models import Timesheet

def week_archive(request, username, year, week,
	template_name='timesheet/week_archive.html'):
	"""Week archive page of timesheet.
	
	:param template_name: Add a custom template.
	"""
	try:
		week_begining = datetime.date(*time.strptime(year + '-0-' + week,
			'%Y-%w-%U')[:3])
		week_ending = week_begining + datetime.timedelta(days=7)
	except ValueError:
		raise Http404
	
	try:
		user = User.objects.get(username__iexact=username)
	except User.DoesNotExist:
		raise Http404
	
	queryset = Timesheet.objects.filter(person=user, date__gte=week_begining,
		date__lt=week_ending).order_by('date', 'time')
	
	timesheet = []
	
	date = week_begining
	while date <= week_ending:
		date_queryset = queryset.filter(date=date)
		timesheet += [{
			'date': date,
			'jobs': date_queryset,
			'hours': date_queryset.aggregate(Sum('hours'))['hours__sum'],
			'pceo': date_queryset.aggregate(Sum('pceo'))['pceo__sum'],
		},]
		date = date + datetime.timedelta(days=1)
	
	week_hours = queryset.aggregate(Sum('hours'))['hours__sum']
	week_pceo = queryset.aggregate(Sum('pceo'))['pceo__sum']
	
	context = {
		'timesheet': timesheet,
		'week_begining': week_begining,
		'week_ending': week_ending,
		'week_hours': week_hours,
		'week_pceo': week_pceo,
	}
	
	return render_to_response(template_name, context,
		context_instance=RequestContext(request))
