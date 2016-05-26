#－*－ coding:utf-8 -*-
import xadmin
from xadmin.layout import *

from models import *
from yt_barcode.views import BatchBarcodeAction


class MaterialAdmin(object):
    model_icon = 'cog'
    hidden_menu = False
    list_display = ('name', 'code', 'category', 'product', 'hardness', 'length','weight', 'owner')
    list_display_links = ('name',)
    list_display_links_details = True

    search_fields = ['name']
    list_filter = ['name', 'category', 'hardness', 'length','weight']
    actions = [BatchBarcodeAction]



class WorkblankAdmin(object):
    model_icon = 'cog'
    hidden_menu = False

    list_display = ('name', 'category', 'hardness', 'length','weight', )

    search_fields = ['name']
    list_filter = ['name', 'category', 'hardness', 'length','weight']
    actions = [BatchBarcodeAction]

xadmin.site.register(Material, MaterialAdmin)
xadmin.site.register(Workblank, WorkblankAdmin)
