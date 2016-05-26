# django imports
from django import template

import permissions.utils
register = template.Library()

class PermissionComparisonNode(template.Node):
    """Implements a node to provide an if current user has passed permission 
    for current object.
    """
    @classmethod
    def handle_token(cls, parser, token):
        bits = token.contents.split()
        if len(bits) != 2:
            raise template.TemplateSyntaxError(
                "'%s' tag takes one argument" % bits[0])
        end_tag = 'endifhasperm'
        nodelist_true = parser.parse(('else', end_tag))
        token = parser.next_token()
        if token.contents == 'else': # there is an 'else' clause in the tag
            nodelist_false = parser.parse((end_tag,))
            parser.delete_first_token()
        else:
            nodelist_false = ""

        return cls(bits[1], nodelist_true, nodelist_false)

    def __init__(self, codename, nodelist_true, nodelist_false):
        self.codename = codename
        self.nodelist_true = nodelist_true
        self.nodelist_false = nodelist_false

    def render(self, context):
        obj = context.get("obj")
        request = context.get("request")
        if permissions.utils.has_permission(obj, request.user, self.codename):
            return self.nodelist_true.render(context)
        else:
            return self.nodelist_false

@register.tag
def ifhasperm(parser, token):
    """This function provides functionality for the 'ifhasperm' template tag.
    """
    return PermissionComparisonNode.handle_token(parser, token)


class PermissionComparisonNodeContentType(template.Node):
    @classmethod
    def handle_token(cls, parser, token):
        bits = token.contents.split()
        if len(bits) != 4:
            raise template.TemplateSyntaxError(
                "'%s' tag takes not 4 argument" % bits[0])
        end_tag = 'endifhasperm_ct'
        nodelist_true = parser.parse(('else', end_tag))
        token = parser.next_token()
        if token.contents == 'else': # there is an 'else' clause in the tag
            nodelist_false = parser.parse((end_tag,))
            parser.delete_first_token()
        else:
            nodelist_false = ""

        return cls(bits[1], bits[2], bits[3], nodelist_true, nodelist_false)

    def __init__(self, codename, content_type_id, object_id, nodelist_true, nodelist_false):
        self.codename = codename
        self.content_type_id = content_type_id
        self.object_id = object_id
        self.nodelist_true = nodelist_true
        self.nodelist_false = nodelist_false

    def render(self, context):
        from django.contrib.contenttypes.models import ContentType
        content_type = ContentType.objects.get(id=self.content_type_id)
        obj = content_type.get_object_for_this_type(pk=self.object_id)
        request = context.get("request")
        if permissions.utils.has_permission(obj, request.user, self.codename):
            return self.nodelist_true.render(context)
        else:
            return self.nodelist_false

@register.tag
def ifhasperm_ct(parser, token):
    """This function provides functionality for the 'ifhasperm' template tag.
    """
    return PermissionComparisonNodeContentType.handle_token(parser, token)


class PermissionComparisonNodeDepartment(template.Node):
    """Implements a node to provide an if current user has passed permission 
    for current object.
    """
    @classmethod
    def handle_token(cls, parser, token):
        bits = token.contents.split()
        if len(bits) != 3:
            raise template.TemplateSyntaxError(
                "'%s' tag takes not 3 argument" % bits[0])
        end_tag = 'endifhasperm_dep'
        nodelist_true = parser.parse(('else', end_tag))
        token = parser.next_token()
        if token.contents == 'else': # there is an 'else' clause in the tag
            nodelist_false = parser.parse((end_tag,))
            parser.delete_first_token()
        else:
            nodelist_false = ""

        return cls(bits[1], bits[2], nodelist_true, nodelist_false)

    def __init__(self, codename, department_name, nodelist_true, nodelist_false):
        self.codename = codename
        self.department_name = department_name.encode("utf-8")
        self.nodelist_true = nodelist_true
        self.nodelist_false = nodelist_false

    def render(self, context):
        from companydepartment.models import Department
        obj = Department.objects.get(name=self.department_name)
        request = context.get("request")
        if permissions.utils.has_permission(obj, request.user, self.codename):
            return self.nodelist_true.render(context)
        else:
            return self.nodelist_false

@register.tag
def ifhasperm_dep(parser, token):
    """This function provides functionality for the 'ifhasperm' template tag.
    """
    return PermissionComparisonNodeDepartment.handle_token(parser, token)
