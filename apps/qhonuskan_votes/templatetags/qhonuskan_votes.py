from django import template
from django.core.urlresolvers import reverse

register = template.Library()


@register.inclusion_tag('qhonuskan/voting_js.html')
def voting_script():
    return {"vote_url": reverse('qhonuskan_vote')}


@register.filter
def is_up_voted_by(object, user):
    """
    If user is up voted given object, it returns True.
    """
    if user.is_authenticated():
        return bool(object.votes.filter(voter=user, value=1).count())
    else:
        return False


@register.filter
def is_down_voted_by(object, user):
    """
    If user is down voted given object, it returns True.
    """
    if user.is_authenticated():
        return bool(object.votes.filter(voter=user, value=-1).count())
    else:
        return False


@register.tag
def vote_buttons_for(parser, token):
    """
    Takes two parameters. The first is the object the votes are for. And the second is
    the template to use. By default it uses vote_buttons.html.

    Usage::
        {% vote_buttons_for idea %}
        {% vote_buttons_for idea "app/follow_form.html" %}
    """
    token_contents = token.split_contents()
    obj = token_contents[1]
    if len(token_contents) > 2:
        template_loc = token_contents[2].replace('"', '').replace("'", '')
    else:
        template_loc = 'qhonuskan/vote_buttons.html'
    return VoteButtonsNode(obj, template_loc)


class VoteButtonsNode(template.Node):
    def __init__(self, obj, template_loc):
        self.obj = obj
        self.template_loc = template_loc

    def render(self, context):
        t = template.loader.get_template(self.template_loc)
        obj = context[self.obj]
        c = {
            "user": context['user'],
            "object": obj,
            "vote_model": "%s.%sVote" % (
                obj._meta.app_label, obj._meta.object_name)
        }
        return t.render(template.Context(c, autoescape=context.autoescape))
