#-*- coding: UTF-8 -*-
import xadmin
from xadmin.plugins.inline import Inline

from models import *
from yt_barcode.views import BatchBarcodeAction


class ContactorInline(object):
    model = Contactor
    extra = 1
    style = 'table'
    exclude = []

class CustomerAdmin(object):
    model_icon = 'cog'
    hidden_menu = False
    list_display = ('name', 'code', 'description', 'address', 'state', 'city', 'telephone', 'mail', 'zip_code', 'importance')
    list_display_links = ('name',)
    list_display_links_details = True
    search_fields = ['name']
    list_filter = ['name', 'address', 'state', 'city', 'importance']

    Inline(Contactor)
    inlines = [ContactorInline]
    actions = [BatchBarcodeAction]
    
class ContactorAdmin(object):
    model_icon = 'cog'
    hidden_menu = False
    list_display = ('name', 'description', 'gender', 'customer', 'note')
    list_display_links = ('name',)
    list_display_links_details = True
    search_fields = ['name']
    list_filter = ['name', 'gender', 'customer',]

xadmin.site.register(Customer, CustomerAdmin)
xadmin.site.register(Contactor, ContactorAdmin)
