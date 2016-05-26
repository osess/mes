#-*- coding:UTF-8 -*-
import xadmin
from xadmin.layout import *
from xadmin.plugins.inline import Inline
from django.utils.translation import ugettext_lazy as _

from models import *
from yt_barcode.views import BatchBarcodeAction

class ProductItemInline(object):
    model = ProductItem
    extra = 2
    style = 'table'

class OrderAdmin(object):
    def cad_codes(self, instance):
        cad_codes_content = ''
        for product_item in instance.product_items.all():
            cad_codes_content += product_item.product.cad_code
            if product_item.product.norm_code:
                cad_codes_content += '|' + product_item.product.norm_code + ' ; '
            else:
                cad_codes_content += ' ; '
        return cad_codes_content
    cad_codes.short_description = _("cad_code")
    cad_codes.allow_tags = True
    cad_codes.is_column = True

    model_icon = 'cog'
    hidden_menu = False
    active_menu="marketing"
    list_display_links = ('contract_code',)
    list_display_links_details = True
    list_display = ('contract_code', 'customer', 'cad_codes', 'order_time', 'status')

    list_filter = ['contract_code', 'customer', 'order_time', 'status']
    search_fields = ['contract_code']

    Inline(ProductItem)
    inlines = [ProductItemInline]

    actions = [BatchBarcodeAction]

    # def list_view(self, request, extra_context=None):
    #     print "==========================="
    #     extra_context=extra_context or dict()
    #     extra_context.update({
    #         'l_m_marketing_active': "active",
    #         })

    #     return super(OrderAdmin, self).changelist_view(request, extra_context)

class ManufactureItemGroupInline(object):
    model = ManufactureItemGroup
    extra = 1
    style = 'table'
    exclude = ['qa_excessive_status', 'productionline', 'is_item_entries_ready']
    
class ManufacturePlanAdmin(object):

    #manufactureplan workflow
    def manufactureplan_workflow(self, instance):
        if not instance.manufactureplan_workflow_status:
            return "<a href='/manufactureplan/manufactureplan_start_workflow/%d/?next=/xadmin/manufactureplan/manufactureplan/'>发起审核流程</a>" % instance.id
        else:
            return "<a href='/manufactureplan/manufactureplan_workflow/%d/?next=/xadmin/manufactureplan/manufactureplan/'>查看审核流程</a>" % instance.id
    manufactureplan_workflow.short_description = _("manufactureplan_workflow")
    manufactureplan_workflow.allow_tags = True
    manufactureplan_workflow.is_column = True

    #create productionlines
    def productionlines(self, instance):
        if instance.manufactureplan_workflow_status == 2:
            if instance.technology_ok:
                if instance.productionlines:
                    return "<a href='/xadmin/manufactureplan/manufactureitemgroup/?_p_manufactureplan__id__exact=%d'>查看生产任务</a>" % instance.id
                else:
                    return "<a href='/manufactureplan/create_productionlines/%d/?next=/xadmin/manufactureplan/manufactureplan/'>创建生产任务</a>" % instance.id
            else:
                return "工艺未就绪"
        else:
            return "审核完可创建"
    productionlines.short_description = _("productionline")
    productionlines.allow_tags = True
    productionlines.is_column = True

    def manufactureplan(self, instance):
        return instance
    manufactureplan.short_description = _("name")
    manufactureplan.allow_tags = True
    manufactureplan.is_column = True

    model_icon = 'cog'
    hidden_menu = False
    active_menu="marketing"
    list_display_links = ('manufactureplan',)
    list_display_links_details = True
    list_display = ('manufactureplan', 'order', 'start_time', 'manufactureplan_workflow', 'productionlines', 'status')

    list_filter = ['order', 'start_time', 'status']
    search_fields = ['order']

    exclude = ['code','name']

    Inline(ManufactureItemGroup)
    inlines = [ManufactureItemGroupInline]

class ManufactureItemGroupAdmin(object):

    #productionline state column
    def action(self, instance):
        return "<a href='/manufactureplan/productionline_states_list/%d/?next=/xadmin/manufactureplan/manufactureitemgroup/'>查看生产进度</a>" % instance.productionline.id
    action.short_description = _("action")
    action.allow_tags = True
    action.is_column = True

    #productionline action column
    def state(self, instance):
        return instance.productionline.get_state_display()
    state.short_description = _("state")
    state.allow_tags = True
    state.is_column = True

    model_icon = 'cog'
    hidden_menu = False
    active_menu="marketing"
    list_display = ('productionline', 'manufactureplan', 'product', 'quantity', 'is_batch', 'batch_code', 'state', 'action', 'is_item_entries_ready')
    list_display_links_details = True

    list_filter = ['product', 'quantity', 'productionline', 'manufactureplan']
    search_fields = ['product']

    exclude = ['qa_excessive_status','productionline']
    actions = [BatchBarcodeAction]

class ManufactureItemAdmin(object):

    def worked_hours(self, instance):
        return instance.worked_hours
    worked_hours.short_description = _("worked_hours")
    worked_hours.allow_tags = True
    worked_hours.is_column = True

    model_icon = 'cog'
    hidden_menu = False
    active_menu="marketing"
    list_display_links = ('code',)
    list_display_links_details = True
    list_display = ('code', 'manu_item_group', 'batch_code', 'worked_hours')

    list_filter = ['code', 'manu_item_group']
    search_fields = ['code', 'manu_item_group']

    exclude = ['qa_excessive_status','productionline']
    actions = [BatchBarcodeAction]

xadmin.site.register(Order, OrderAdmin)
xadmin.site.register(ManufacturePlan, ManufacturePlanAdmin)
xadmin.site.register(ManufactureItemGroup, ManufactureItemGroupAdmin)
xadmin.site.register(ManufactureItem, ManufactureItemAdmin)




# class ProductItemAdmin(object):
#     def norm_code(self, instance):
#         return instance.product.norm_code
#     norm_code.short_description = _("norm_code")
#     norm_code.allow_tags = True
#     norm_code.is_column = True

#     model_icon = 'cog'
#     hidden_menu = False
#     list_display_links = ('code',)
#     list_display_links_details = True
#     list_display = ('order', 'product', 'norm_code', 'quantity', 'unit_price', 'finish_time')

#     list_filter = ['product', 'quantity', 'order' ]
#     search_fields = ['product']

# xadmin.site.register(ProductItem, ProductItemAdmin)


# class OperationGroupRecordInline(object):
#     model = OperationGroupRecord
#     extra = 1
#     style = 'tab'

# class ProductionLineAdmin(object):

#     #productionline state column
#     def action(self, instance):
#         return "<a href='/manufactureplan/productionline_states_list/%d/?next=/xadmin/manufactureplan/manufactureitemgroup/?_p_manufactureplan__id__exact=%d'>查看生产进度</a>" %(instance.id, instance.manufactureplan.id)
#     action.short_description = _("action")
#     action.allow_tags = True
#     action.is_column = True

#     model_icon = 'cog'
#     hidden_menu = False
#     list_display_links = ('state',)
#     list_display = ('technology', 'state', 'action')

#     list_filter = ['technology',  'state', 'date_added',]
#     search_fields = ['technology']
#     list_display_links_details = True
    
#     Inline(OperationGroupRecord)
#     inlines = [OperationGroupRecordInline]

# xadmin.site.register(ProductionLine, ProductionLineAdmin)


# class OperationGroupRecordAdmin(object):

#     model_icon = 'cog'
#     hidden_menu = False
#     list_display_links = ('operation_group',)
#     list_display_links_details = True
#     list_display = ('productionline', 'operation_group', 'device_items')

#     list_filter = ['productionline', 'operation_group', 'device_items']
#     search_fields = ['productionline', 'operation_group']

# xadmin.site.register(OperationGroupRecord, OperationGroupRecordAdmin)


# class OperationRecordAdmin(object):

#     model_icon = 'cog'
#     hidden_menu = False
#     list_display_links = ('status',)
#     list_display_links_details = True
#     list_display = ('oper_group_record', 'operation', 'status', 'knife_items', 'tool_items')


#     list_filter = ['oper_group_record', 'operation', 'status']
#     search_fields = ['oper_group_record', 'operation']

# xadmin.site.register(OperationRecord, OperationRecordAdmin)


# class ManufactureRecordAdmin(object):

#     model_icon = 'cog'
#     hidden_menu = False
#     list_display = (
#         'operation_record', 'manufacture_item', 'status',)

#     list_filter = ['operation_record', 'manufacture_item', 'status']
#     search_fields = ['manufacture_item']

# xadmin.site.register(ManufactureRecord, ManufactureRecordAdmin)


# class QARecordAttributeInline(object):
#     model = QARecordAttribute
#     extra = 1
#     style = 'table'

# class QARecordAdmin(object):

#     model_icon = 'cog'
#     hidden_menu = False
#     list_display_links = ('note',)
#     list_display_links_details = True


#     exclude = ['qa_excessive_status',]

#     list_display = (
#        'employee', 'operation_record', 'manufacture_item', 'attributes', 'type', 'created_at',
#        'updated_at')

#     list_filter = ['employee', 'operation_record', 'manufacture_item', 'attributes', 'type', 'created_at',
#        'updated_at']
#     search_fields = ['employee', 'manufacture_item']

#     Inline(QARecordAttribute)
#     inlines = [QARecordAttributeInline]

# xadmin.site.register(QARecord, QARecordAdmin)


# class QARecordAttributeAdmin(object):

#     model_icon = 'cog'
#     hidden_menu = False

#     list_display = (
#        'qa_record', 'attribute', 'display_value', 'absolute_value',
#        'is_published', )

#     list_filter = ['qa_record', 'attribute', 'display_value', 'absolute_value',
#        'is_published', ]
#     search_fields = ['qa_record', 'attribute']

# xadmin.site.register(QARecordAttribute, QARecordAttributeAdmin)