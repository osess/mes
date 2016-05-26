#-*- coding: UTF-8 -*- 
import xadmin
from models import *


class PostAdmin(object):
    model_icon = 'cog'
    hidden_menu = False
    list_display = ('section', 'title', 'slug', 'address', 'markup', 'description', 'primary_image', 'state')
    list_display_links = ('title',)
    list_display_links_details = True
    search_fields = ['title']
    #list_filter = ['name', 'address', 'state', 'city', 'importance']

    #Inline(Contactor)
    #inlines = [ContactorInline]
    #actions = [BatchBarcodeAction]

xadmin.site.register(Post)

# from django.contrib.auth.models import User
# class UserAdmin(object):
#     list_display = ('username', 'last_name', 'first_name', 'email', 'is_staff','is_active', 'last_login')
#     list_display_links = ('username',)
#     list_display_links_details = True

#     list_filter = ['username', 'last_name', 'first_name', 'email', 'is_staff','is_active', 'last_login']
#     search_fields = ['username', 'last_name', 'first_name', 'email', 'is_staff','is_active', 'last_login']
#     exclude = ['is_superuser', 'user_permissions']

# xadmin.site.register(User, UserAdmin)