#-*- coding: UTF-8 -*-
from django import template
from django.utils.translation import ugettext_lazy as _

register = template.Library()

@register.simple_tag
def get_quality_report_content(productionline,type="first",page_num=0):
	oper_group_records = productionline.first_child_productionline.oper_group_records.all()
	contents = []
	first_step = 7
	step = 9
	if type == "first":
		for i in range(first_step):
			try:
				oper_group_record = oper_group_records[i]
			except:
				oper_group_record = None
			contents.extend(get_oper_group_record_content(oper_group_record))

	elif type == "others":
		for i in range(page_num*step+first_step,(page_num+1)*step+first_step):
			try:
				oper_group_record = oper_group_records[i]
			except:
				oper_group_record = None
			contents.extend(get_oper_group_record_content(oper_group_record))

	return "".join(contents)

def get_oper_group_record_content(oper_group_record):
	oper_contents = []
	if oper_group_record:
		oper_contents.append("<tr>")
		oper_contents.append("<td>%d</td>"%oper_group_record.operation_group.order)
		oper_contents.append("<td>%s</td>"%(oper_group_record.operation_group.Job.position.name if oper_group_record.operation_group.Job else ""))
		oper_contents.append("<td></td>")
		oper_contents.append("<td>%s</td>"%(oper_group_record.last_operation_record.qa_first_self.employee.user if oper_group_record.last_operation_record.qa_first_self else ""))
		oper_contents.append("<td>%s</td>"%(oper_group_record.last_operation_record.qa_first_double.employee.user if oper_group_record.last_operation_record.qa_first_double else ""))
		oper_contents.append("<td>%s</td>"%(oper_group_record.last_operation_record.qa_first_inspector.employee.user if oper_group_record.last_operation_record.qa_first_inspector else ""))
		oper_contents.append("<td></td>")
		oper_contents.append("<td></td>")
		oper_contents.append("<td></td>")
		oper_contents.append("<td></td>")
		oper_contents.append("<td>&nbsp;</td>")
		oper_contents.append("</tr>")
		oper_contents.append("<tr>")
		oper_contents.append("<td></td>"*11)
		oper_contents.append("</tr>")
	else:
		oper_contents.append(("<tr>"+"<td>&nbsp;</td>"*11+"</tr>")*2)
	return oper_contents
