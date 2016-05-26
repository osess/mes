from models import Timesheet

import xadmin


class TimesheetAdmin(object):
    model_icon = 'cog'
    hidden_menu = False
    list_display = (
       'person', 'start', 'date', 'end',
       'type',)

    list_filter = ['person', 'start', 'date', 'end',
       'type']
    search_fields = ['person', 'start', 'date', 'end',
       'type']

xadmin.site.register(Timesheet, TimesheetAdmin)