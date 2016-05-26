#-*- coding: UTF-8 -*-
import xadmin
from xadmin.layout import *
from xadmin.plugins.inline import Inline
from django.utils.translation import ugettext_lazy as _

from models import Maintenance



class MaintenanceAdmin(object):

    model_icon = 'cog'
    hidden_menu = False
    active_menu = "storage"
    list_display = (
        'device', 'date', 'project', 'status', 'maintainer', 'applicat')

    list_filter = ['device', 'date', 'project', 'status', 'maintainer', 'applicat']
    search_fields = ['device', 'date', 'project', 'status', 'maintainer', 'applicat']



xadmin.site.register(Maintenance, MaintenanceAdmin)