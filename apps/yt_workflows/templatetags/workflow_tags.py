from django import template  
from django.contrib.auth.models import User
from permissions.models import Permission,PrincipalRoleRelation
from workflows.models import State,StatePermissionRelation
from django.shortcuts import get_object_or_404

register = template.Library()

@register.simple_tag
def has_permission(the_dict, key):
   # Try to fetch from the dict, and if it's not found return an empty string.
   return the_dict.get(key, '')
   
   
@register.simple_tag
def state_users(state):
    users_name = ''
    permission = get_object_or_404(Permission, codename = "edit")
    statepermissionrelations = StatePermissionRelation.objects.filter(permission_id = permission.id,state_id = state.id)
    for statepermissionrelation in statepermissionrelations:
        principalrolerelations = PrincipalRoleRelation.objects.filter(role_id = statepermissionrelation.role_id)
        for principalrolerelation in principalrolerelations:
            user = get_object_or_404(User, id = principalrolerelation.user_id)
            if not user.is_superuser:
                users_name = users_name+user.username+'<br>'
                
    return users_name

