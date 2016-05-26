'''
Created on Jan 14, 2011

@author: peterm
'''
from warehouse.models import Location
from django import template
register = template.Library()
from report.views import convert_special_character


# #by lxy


@register.simple_tag
def convert_special_character_tag(string):

    #string = _("bom list")

    return convert_special_character(string)