from django.template import Library, Node

from announcements.models import current_announcements_for_request


register = Library()


class FetchAnnouncementsNode(Node):
    def __init__(self, context_var, limit=None):
        self.context_var = context_var
        self.limit = limit
    
    def render(self, context):
        try:
            request = context["request"]
        except KeyError:
            raise Exception("{% fetch_announcements %} requires the HttpRequest in context.")
        kwargs = {}
        announcements = current_announcements_for_request(request, **kwargs)
        if self.limit:
            announcements = announcements[:self.limit]
        context[self.context_var] = announcements
        return ""

@register.tag
def fetch_announcements(parser, token):
    bits = token.split_contents()
    # @@@ very naive parsing
    if len(bits) == 5:
        limit = bits[2]
        context_var = bits[4]
    elif len(bits) == 3:
        limit = None
        context_var = bits[2]
    return FetchAnnouncementsNode(context_var, limit)
