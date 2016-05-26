#-*- coding: UTF-8 -*-
import xadmin

from models import Company, Department


class CompanyAdmin(object):
    model_icon = 'cog'
    hidden_menu = False
    list_display = (
       'name', 'parent', 'description', 'address',
       'city', 'state', 'zip_code', 'importance',
       'date_modified')

    list_filter = ['name', 'parent', 'description', 'address',
       'city', 'state', 'zip_code', 'importance',
       'date_modified']
    search_fields = ['name']


class DepartmentAdmin(object):
    model_icon = 'cog'
    hidden_menu = False
    list_display = (
       'name', 'belong_to', 'parent', 'description',
       'importance',  'date_modified')

    list_filter = ['name', 'belong_to', 'parent', 'description',
       'importance',  'date_modified']
    search_fields = ['name']


xadmin.site.register(Company, CompanyAdmin)
xadmin.site.register(Department, DepartmentAdmin)
