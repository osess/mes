#-*- coding: UTF-8 -*- 
import xadmin
from actstream.models import Action


class ActionAdmin(object):
    list_display = ('actor', 'verb', 'target', 'description', 'timestamp', 'public')
    list_display_links = ('actor',)
    search_fields = ['actor', 'verb', 'target', 'description']
    list_filter = ['description', 'timestamp', 'public']

xadmin.site.register(Action, ActionAdmin)