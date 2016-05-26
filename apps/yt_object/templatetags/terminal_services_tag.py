from django.template import Library
from django.utils.translation import ugettext_lazy as _
from datetime import date
from settings import terminal_date
register = Library()


@register.assignment_tag(takes_context=True)
def terminal_services(context):
    if date.today() >= terminal_date:
        return False
    else:
        return True