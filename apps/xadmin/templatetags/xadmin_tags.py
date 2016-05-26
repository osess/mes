from django.template import Library
from xadmin.util import static, vendor as util_vendor

register = Library()


@register.simple_tag(takes_context=True)
def view_block(context, block_name, *args, **kwargs):
    if 'admin_view' not in context:
        return ""

    admin_view = context['admin_view']
    nodes = []
    method_name = 'block_%s' % block_name

    for view in [admin_view] + admin_view.plugins:
        if hasattr(view, method_name) and callable(getattr(view, method_name)):
            block_func = getattr(view, method_name)
            result = block_func(context, nodes, *args, **kwargs)
            if result and type(result) in (str, unicode):
                nodes.append(result)
    if nodes:
        return ''.join(nodes)
    else:
        return ""


@register.filter
def admin_urlname(value, arg):
    return 'admin:%s_%s_%s' % (value.app_label, value.module_name, arg)

static = register.simple_tag(static)


@register.simple_tag(takes_context=True)
def vendor(context, *tags):
    return util_vendor(*tags).render()




#by lxy
from django.utils.translation import ugettext_lazy as _

@register.filter(name='trans_to_table')
def trans_to_table(value): # Only one argument.

    if value.field_name == 'product':
        table = '%s</td><td>%s</td><td>%s</td><td>%s' %(value.obj.product.name, value.obj.product.cad_code, value.obj.product.norm_code, value.obj.product.symbol)
        return table
    return value.val


