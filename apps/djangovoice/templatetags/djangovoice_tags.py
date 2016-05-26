from django.template import Library, Node, Variable, TemplateSyntaxError
from djangovoice.compat import gravatar_for_user
from djangovoice.models import Type, Status

register = Library()


class TypeListNode(Node):
    def render(self, context):
        context['type_list'] = Type.objects.all()
        return ''


def build_type_list(parser, token):
    """
    {% get_type_list %}
    """
    return TypeListNode()

register.tag('get_type_list', build_type_list)


class StatusListNode(Node):
    def __init__(self, list_type):
        self.list_type = Variable(list_type)

    def render(self, context):
        list_type = self.list_type.resolve(context)
        status_list = Status.objects.all()

        if list_type in ['open', 'closed']:
            status = list_type  # values are same.
            status_list = status_list.filter(status=status)

        context['status_list'] = status_list
        return ''


def build_status_list(parser, token):
    """
    {% get_status_list %}
    """
    bits = token.contents.split()

    if len(bits) != 2:
        msg = "'%s' tag takes exactly 1 arguments" % bits[0]
        raise TemplateSyntaxError(msg)

    return StatusListNode(bits[1])

register.tag('get_status_list', build_status_list)


@register.filter
def display_name(user):
    """
    If user has full name, get user's full name, else username.
    """
    full_name = user.get_full_name()
    if not full_name:
        return user.username

    return full_name


@register.inclusion_tag('djangovoice/tags/widget.html', takes_context=True)
def djangovoice_widget(context):
    arguments = {'STATIC_URL': context.get('STATIC_URL')}

    return arguments


@register.simple_tag
def get_user_image(user, size=80):
    url = gravatar_for_user(user, size)
    return '<img src="%s" alt="%s" height="%s" width="%s" />' % (
        url, user.username, size, size)
