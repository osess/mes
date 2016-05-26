#-*- coding: UTF-8 -*-
from django import template
from django.utils.translation import ugettext_lazy as _

register = template.Library()

@register.simple_tag
def set_wrap(content,word_num=0):
	content = unicode(content)
	if 25 < len(content):
		return content[:25] + "  " + content[25:]
	else:
		return content


@register.simple_tag
def convert_special_character_tag_to_rml(string):
	from yt_report.views import convert_special_character_to_rml
	modified_string = convert_special_character_to_rml(string)
	return modified_string