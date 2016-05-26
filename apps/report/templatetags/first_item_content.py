#-*- coding: UTF-8 -*-
from django import template
from django.utils.translation import ugettext_lazy as _

register = template.Library()

@register.simple_tag
def get_first_item_content(productionline,type="html"):
	contents = []
	sum_line = 0
	for oper_group_record in productionline.first_child_productionline.oper_group_records.all():
		qa_self_record_attributes      = oper_group_record.last_operation_record.qa_first_self.qa_record_attributes.all() if oper_group_record.last_operation_record.qa_first_self else []
		qa_double_record_attributes    = oper_group_record.last_operation_record.qa_first_double.qa_record_attributes.all() if oper_group_record.last_operation_record.qa_first_double else []
		qa_inspector_record_attributes = oper_group_record.last_operation_record.qa_first_inspector.qa_record_attributes.all() if oper_group_record.last_operation_record.qa_first_inspector else []
		counts = max(len(qa_self_record_attributes),len(qa_double_record_attributes),len(qa_inspector_record_attributes))
		step = 4
		rowspan_count = (counts/step+1)*3 if counts%step else (counts/step)*3 if counts != 0 else 3
		sum_line += rowspan_count
		line_count = 0
		while True:
			contents.append("<tr>")
			if line_count == 0:
				contents.append("<td rowspan='%d'>%d</td>"%(rowspan_count,oper_group_record.operation_group.order))
				contents.append("<td rowspan='%d'>%s</td>"%(rowspan_count,(oper_group_record.operation_group.Job.position.name if oper_group_record.operation_group.Job else "")))
			elif type == "rml":
				contents.append("<td>&nbsp;</td>")
				contents.append("<td>&nbsp;</td>")
			for i in range(line_count,line_count+step):
				try:
					qa_record_attribute = qa_self_record_attributes[i]
				except:
					qa_record_attribute = None
				if qa_record_attribute:
					contents.append("<td>%s</td>"%qa_record_attribute.product_attribute.absolute_value)
					contents.append("<td>%s</td>"%qa_record_attribute.absolute_value)
				else:
					contents.append("<td>&nbsp;</td>")
					contents.append("<td>&nbsp;</td>")
			if line_count == 0:
				contents.append("<td colspan='2'>%s</td>"%_("QASelfRecord").encode('utf-8'))
				contents.append("<td colspan='3'>%s</td>"%(oper_group_record.last_operation_record.qa_first_self.employee.user if oper_group_record.last_operation_record.qa_first_self else ""))
			else:
				contents.append("<td colspan='2'>%s</td>"%_("QASelfRecord").encode('utf-8'))
				contents.append("<td colspan='3'></td>")
			contents.append("</tr>")

			contents.append("<tr>")
			if type == "rml":
				contents.append("<td>&nbsp;</td>")
				contents.append("<td>&nbsp;</td>")
			for i in range(line_count,line_count+step):
				try:
					qa_record_attribute = qa_double_record_attributes[i]
				except:
					qa_record_attribute = None
				if qa_record_attribute:
					contents.append("<td>%s</td>"%qa_record_attribute.product_attribute.absolute_value)
					contents.append("<td>%s</td>"%qa_record_attribute.absolute_value)
				else:
					contents.append("<td>&nbsp;</td>")
					contents.append("<td>&nbsp;</td>")
			if line_count == 0:
				contents.append("<td colspan='2'>%s</td>"%_("QADoubleRecord").encode('utf-8'))
				contents.append("<td colspan='3'>%s</td>"%(oper_group_record.last_operation_record.qa_first_double.employee.user if oper_group_record.last_operation_record.qa_first_double else ""))
			else:
				contents.append("<td colspan='2'>%s</td>"%_("QADoubleRecord").encode('utf-8'))
				contents.append("<td colspan='3'></td>")
			contents.append("</tr>")

			contents.append("<tr>")
			if type == "rml":
				contents.append("<td>&nbsp;</td>")
				contents.append("<td>&nbsp;</td>")
			for i in range(line_count,line_count+step):
				try:
					qa_record_attribute = qa_inspector_record_attributes[i]
				except:
					qa_record_attribute = None
				if qa_record_attribute:
					contents.append("<td>%s</td>"%qa_record_attribute.product_attribute.absolute_value)
					contents.append("<td>%s</td>"%qa_record_attribute.absolute_value)
				else:
					contents.append("<td>&nbsp;</td>")
					contents.append("<td>&nbsp;</td>")
			if line_count == 0:
				contents.append("<td colspan='2'>%s</td>"%_("QAInspectorRecord").encode('utf-8'))
				contents.append("<td colspan='3'>%s</td>"%(oper_group_record.last_operation_record.qa_first_inspector.employee.user if oper_group_record.last_operation_record.qa_first_inspector else ""))
			else:
				contents.append("<td colspan='2'>%s</td>"%_("QAInspectorRecord").encode('utf-8'))
				contents.append("<td colspan='3'></td>")
			contents.append("</tr>")

			line_count += step
			if line_count >= counts:
				break
	if type == "rml" and ((sum_line + 6) % 29) != 0:
		for i in range(29 - (sum_line + 6) % 29):
			contents.append("<tr><td>&nbsp;</td>"+"<td></td>"*11+"</tr>")
	return "".join(contents)