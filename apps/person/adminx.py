#-*- coding: UTF-8 -*- 
import xadmin
from models import *


class BenefitTypeAdmin(object):
    list_display = ('name', 'display_name', 'code', 'category', 'appear_on_payslip', 'active', 'order', 'amount_fix', 'amount_percentage', 'amount_code', 'placeholder', 'note')
    list_display_links = ('name',)
    search_fields = ['name']
    list_filter = ['name', 'code', 'category', 'active', 'order', 'amount_fix', 'amount_code']

class PositionAdmin(object):
    list_display = ('name', 'importance', 'private_description', 'public_description')
    list_display_links = ('name',)
    search_fields = ['name']
    list_filter = ['name', 'importance']

class JobAdmin(object):
    list_display = ('status', 'published_status', 'pay', 'benefits', 'department', 'position', 'location', 'slug', 'num_of_planed_employees', 'num_of_vacancies', 'note')
    list_display_links = ('name',)
    search_fields = ['name']
    list_filter = ['status', 'published_status', 'pay', 'benefits', 'department', 'position', 'location']

class EmployeeAdmin(object):
    list_display = ('name', 'user', 'description', 'gender', 'internal_id', 'department', 'job', 'join_date', 'note')
    list_display_links = ('name',)
    search_fields = ['name']
    list_filter = ['name', 'user', 'gender', 'department', 'job', 'internal_id', 'join_date',]

class UserPlainPasswordAdmin(object):
    list_display = ('username', 'password')
    list_display_links = ('username',)
    search_fields = ['username']
    list_filter = ['username', 'password']
    list_display_links_details = True

xadmin.site.register(BenefitType, BenefitTypeAdmin)
xadmin.site.register(Position, PositionAdmin)
xadmin.site.register(Job, JobAdmin)
xadmin.site.register(Employee, EmployeeAdmin)
xadmin.site.register(UserPlainPassword, UserPlainPasswordAdmin)

# from django.contrib.auth.models import User
# class UserAdmin(object):
#     list_display = ('username', 'last_name', 'first_name', 'email', 'is_staff','is_active', 'last_login')
#     list_display_links = ('username',)
#     list_display_links_details = True

#     list_filter = ['username', 'last_name', 'first_name', 'email', 'is_staff','is_active', 'last_login']
#     search_fields = ['username', 'last_name', 'first_name', 'email', 'is_staff','is_active', 'last_login']
#     exclude = ['is_superuser', 'user_permissions']

# xadmin.site.register(User, UserAdmin)