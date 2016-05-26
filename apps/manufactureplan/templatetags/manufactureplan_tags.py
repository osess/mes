from django import template  
from django.contrib.auth.models import User
from permissions.models import Permission,PrincipalRoleRelation
from workflows.models import State,StatePermissionRelation
from manufactureplan.models import ProductionLine, OperationGroupRecord, OperationRecord
from warehouse.models import DeviceEntry
from django.template import Library, Node, VariableDoesNotExist

register = template.Library()

@register.filter
def current_manufacture_items(device_entry_id, productionline_id):
    # device_entry = DeviceEntry.objects.get(id=device_entry_id)
    # productionline = ProductionLine.objects.get(id=productionline_id)
    # current_manufacture_items = []
    # for manufacture_item in productionline.self_manufacture_items:
    #     if device_entry in manufacture_item.current_operation_record.oper_group_record.device_items.all():
    #         current_manufacture_items.append(manufacture_item)
    print device_entry_id
    return device_entry_id


@register.tag(name="switch")
def do_switch(parser, token):
    """
    The ``{% switch %}`` tag compares a variable against one or more values in
    ``{% case %}`` tags, and outputs the contents of the matching block.  An
    optional ``{% else %}`` tag sets off the default output if no matches
    could be found::

        {% switch result_count %}
            {% case 0 %}
                There are no search results.
            {% case 1 %}
                There is one search result.
            {% else %}
                Jackpot! Your search found {{ result_count }} results.
        {% endswitch %}

    Each ``{% case %}`` tag can take multiple values to compare the variable
    against::

        {% switch username %}
            {% case "Jim" "Bob" "Joe" %}
                Me old mate {{ username }}! How ya doin?
            {% else %}
                Hello {{ username }}
        {% endswitch %}
    """
    bits = token.contents.split()
    tag_name = bits[0]
    if len(bits) != 2:
        raise template.TemplateSyntaxError("'%s' tag requires one argument" % tag_name)
    variable = parser.compile_filter(bits[1])

    class BlockTagList(object):
        # This is a bit of a hack, as it embeds knowledge of the behaviour
        # of Parser.parse() relating to the "parse_until" argument.
        def __init__(self, *names):
            self.names = set(names)
        def __contains__(self, token_contents):
            name = token_contents.split()[0]
            return name in self.names

    # Skip over everything before the first {% case %} tag
    parser.parse(BlockTagList('case', 'endswitch'))

    cases = []
    token = parser.next_token()
    got_case = False
    got_else = False
    while token.contents != 'endswitch':
        nodelist = parser.parse(BlockTagList('case', 'else', 'endswitch'))
        
        if got_else:
            raise template.TemplateSyntaxError("'else' must be last tag in '%s'." % tag_name)

        contents = token.contents.split()
        token_name, token_args = contents[0], contents[1:]
        
        if token_name == 'case':
            tests = map(parser.compile_filter, token_args)
            case = (tests, nodelist)
            got_case = True
        else:
            # The {% else %} tag
            case = (None, nodelist)
            got_else = True
        cases.append(case)
        token = parser.next_token()

    if not got_case:
        raise template.TemplateSyntaxError("'%s' must have at least one 'case'." % tag_name)

    return SwitchNode(variable, cases)

class SwitchNode(Node):
    def __init__(self, variable, cases):
        self.variable = variable
        self.cases = cases

    def __repr__(self):
        return "<Switch node>"

    def __iter__(self):
        for tests, nodelist in self.cases:
            for node in nodelist:
                yield node

    def get_nodes_by_type(self, nodetype):
        nodes = []
        if isinstance(self, nodetype):
            nodes.append(self)
        for tests, nodelist in self.cases:
            nodes.extend(nodelist.get_nodes_by_type(nodetype))
        return nodes

    def render(self, context):
        try:
            value_missing = False
            value = self.variable.resolve(context, True)
        except VariableDoesNotExist:
            no_value = True
            value_missing = None
        
        for tests, nodelist in self.cases:
            if tests is None:
                return nodelist.render(context)
            elif not value_missing:
                for test in tests:
                    test_value = test.resolve(context, True)
                    if value == test_value:
                        return nodelist.render(context)
        else:
            return ""

            
'''
@register.simple_tag
def productionline_detail(productionline):
    productionline_detail_content = ''
    operation_group_records = OperationGroupRecord.objects.filter(productionline=productionline).order_by('operation_group__order')
    for operation_group_record in operation_group_records:
        productionline_detail_content = productionline_detail_content+"<table class='table table-bordered span2'>"
        productionline_detail_content = productionline_detail_content+"<th>"+operation_group_record.code+"</th>"
        operation_records = OperationRecord.objects.filter(oper_group_record=operation_group_record).order_by('operation__order')
        for operation_record in operation_records:
            if operation_record.status == 1:
                productionline_detail_content = productionline_detail_content+"<tr><td>"
            elif operation_record.status == 2:
                productionline_detail_content = productionline_detail_content+"<tr bgcolor='#FFFF00'><td>"
            elif operation_record.status == 3:
                productionline_detail_content = productionline_detail_content+"<tr bgcolor='#FF0000'><td>"
            elif operation_record.status == 4:
                productionline_detail_content = productionline_detail_content+"<tr bgcolor='#00FF00'><td>"
            elif operation_record.status == 5:
                productionline_detail_content = productionline_detail_content+"<tr bgcolor='#00FF00'><td>"
            elif operation_record.status == 6:
                productionline_detail_content = productionline_detail_content+"<tr bgcolor='#00FF00'><td>"
            else:
                productionline_detail_content = productionline_detail_content+"<tr><td>"
            productionline_detail_content = productionline_detail_content+operation_record.code
            productionline_detail_content = productionline_detail_content+"</td></tr>"
            
        productionline_detail_content = productionline_detail_content+"</table>"
    return productionline_detail_content
'''
