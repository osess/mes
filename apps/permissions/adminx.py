#-*- coding: UTF-8 -*-
import xadmin

from models import Permission, Role, ObjectPermission, ObjectPermissionInheritanceBlock, PrincipalRoleRelation


class PermissionAdmin(object):
    model_icon = 'cog'
    hidden_menu = False
    list_display = ('name', 'codename')

    list_filter = ['name', 'codename']
    search_fields = ['name']


class RoleAdmin(object):
    model_icon = 'cog'
    hidden_menu = False
    list_display = ('name', )

    list_filter = ['name']
    search_fields = ['name']


class ObjectPermissionAdmin(object):
    model_icon = 'cog'
    hidden_menu = False
    list_display = ('role', 'permission')

    list_filter = ['role', 'permission']
    search_fields = ['role']


class ObjectPermissionInheritanceBlockAdmin(object):
    model_icon = 'cog'
    hidden_menu = False
    list_display = ('permission', )

    list_filter = ['permission', ]
    search_fields = ['role']



class PrincipalRoleRelationAdmin(object):
    model_icon = 'cog'
    hidden_menu = False
    list_display = ('user', 'group', 'role')

    list_filter = ['user', 'group', 'role']
    search_fields = ['role']




xadmin.site.register(Permission, PermissionAdmin)
xadmin.site.register(Role, RoleAdmin)
xadmin.site.register(ObjectPermission, ObjectPermissionAdmin)
xadmin.site.register(ObjectPermissionInheritanceBlock, ObjectPermissionInheritanceBlockAdmin)
xadmin.site.register(PrincipalRoleRelation, PrincipalRoleRelationAdmin)
