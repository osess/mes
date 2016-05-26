import xadmin
from models import UserSettings
from xadmin.layout import *

from django.contrib.sites.models import Site


class UserSettingsAdmin(object):
    model_icon = 'cog'
    hidden_menu = True
xadmin.site.register(UserSettings, UserSettingsAdmin)

'''
class SiteAdmin(object):
    model_icon = 'cog'
    #hidden_menu = True
    list_display =('domain','name')
xadmin.site.register(Site, SiteAdmin)
'''