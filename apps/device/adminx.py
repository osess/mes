#-*- coding: UTF-8 -*- 
from django.utils.translation import ugettext_lazy as _
import xadmin
from xadmin.layout import *
from xadmin.plugins.inline import Inline

from models import *
from yt_barcode.views import BatchBarcodeAction


class DeviceAdmin(object):

    model_icon = 'cog'
    hidden_menu = False
    list_display = ('name', 'prefix', 'type', 'description', 'producter', 'desigen_lifetime',)
    list_display_links = ('name',)
    list_display_links_details = True

    list_filter = ['name', 'type', 'producter', 'desigen_lifetime',]
    search_fields = ['name']
    actions = [BatchBarcodeAction]


class ToolAdmin(object):

    model_icon = 'cog'
    hidden_menu = False
    list_display = ('prefix', 'name', 'norm', 'producter', 'type')
    list_display_links = ('name',)
    list_display_links_details = True

    list_filter = ['name', 'norm', 'producter', 'type']
    search_fields = ['name', 'norm']
    actions = [BatchBarcodeAction]

class KnifeAttributeInline(object):
    model = KnifeAttribute
    extra = 1
    style = 'table'
    exclude = []


from django.db.models import Count
class KnifeAdmin(object):
    def display_unicode(self, instance):
        return instance.__unicode__()
    display_unicode.short_description = _("code")
    display_unicode.allow_tags = True
    display_unicode.is_column = True

    def attributes_values(self, instance):
        return instance.attributes_values
    attributes_values.short_description = _("attribute")
    attributes_values.allow_tags = True
    attributes_values.is_column = True

    def product_format():
        knife_attributes = KnifeAttribute.objects.values('attribute').annotate(attribute_count=Count('attribute')).order_by('attribute__ext_code')
        attribute_ids = [attribute['attribute'] for attribute in knife_attributes]

        attribute_functions = []
        for attribute_id in attribute_ids:
            function_name = "attribute_%d_function" %(attribute_id)
            generate_function_string = '''
def attribute_%d_function(self, instance):
    attribute_value = instance.knife_attributes.get(attribute_id=%d).value
    return attribute_value
''' %(attribute_id, attribute_id)
            attribute_functions.append([function_name, generate_function_string, attribute_id])

        return attribute_functions


    list_display = ('name', 'desigen_lifetime')
    list_display = list(list_display)
    attribute_functions = product_format()
    product_catalog_attribute = Attribute.objects.all()

    for i, function in enumerate(attribute_functions):
        function_name = function[0]
        generate_function_string = function[1]
        function_attribute_id = function[2]
        attribute_name = product_catalog_attribute.get(id = function_attribute_id)

        short_description_string = "%s.short_description = '%s'" %(function_name, attribute_name)
        exec(function[1])
        exec(short_description_string)
        list_display.insert(i+1, function[0])


    list_display = tuple(list_display)

    model_icon = 'cog'
    hidden_menu = False

    list_display_links = ('name',)
    list_display_links_details = True

    list_filter = ['name', 'prefix', 'desigen_lifetime']
    search_fields = ['name', 'prefix', 'desigen_lifetime']

    Inline(KnifeAttribute)
    inlines = [KnifeAttributeInline]
    actions = [BatchBarcodeAction]
    
class KnifeAttributeAdmin(object):
    
    model_icon = 'cog'
    hidden_menu = False
    list_display = ('knife', 'attribute', 'value', 'attribute_code', )

    list_filter = ['knife', 'attribute', 'value', 'attribute_code']
    search_fields = ['knife']

xadmin.site.register(Device, DeviceAdmin)
xadmin.site.register(Tool, ToolAdmin)
xadmin.site.register(Knife, KnifeAdmin)
xadmin.site.register(KnifeAttribute, KnifeAttributeAdmin)

