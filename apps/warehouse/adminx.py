#-*- coding: UTF-8 -*-
import xadmin
from xadmin.layout import *
from xadmin.plugins.inline import Inline
from django.utils.translation import ugettext_lazy as _

from models import *
from models import (DeviceEntry, ElectricityCharge, Expense, 
    TransferList, TransportList, TransportListDetail, EntryLog)
from yt_barcode.views import BatchBarcodeAction

class LocationAdmin(object):
    model_icon = 'cog'
    hidden_menu = False
    show_bookmarks = False
    active_menu = "storage"
    list_display = ('name', 'type', 'code', 'description','lon', 'lat', 
        'created_at', 'updated_at','updated_by'
    )
    list_display_links = ('name',)
    list_display_links_details = True

    list_filter = ['name', 'code', 'description', 'lon', 'lat', 
        'created_at', 'updated_at', 'updated_by'
    ]
    search_fields = ['name']
    exclude = ['type']

class ItemAdmin(object):
    model_icon = 'cog'
    hidden_menu = False
    active_menu = "storage"
    show_bookmarks = False
    list_display = ('content_type','content_object',)
    list_display_links_details = True

    list_filter = ['content_type',]
    search_fields = ['content_type']

class BomEntryAdmin(object):
    model_icon = 'cog'
    hidden_menu = False
    active_menu = "storage"
    show_bookmarks = False
    list_display = (
        'parent', 'productionline', 'item', 'unit', 'qty', 'created_at', 
        'state', 'note', 'updated_by',)
    list_display_links_details = True

    list_filter = ['parent', 'productionline', 'item', 'unit', 'qty', 'created_at',
        'state', 'note', 'updated_by']
    search_fields = ['parent', 'item']

class ItemJournalAdmin(object):

    model_icon = 'cog'
    hidden_menu = False
    active_menu = "storage"
    show_bookmarks = False
    list_display = (
        'journal_type', 'note', 'updated_by', )

    list_filter = ['journal_type', 'note', 'updated_by']
    search_fields = ['journal_type']


class ItemEntryAdmin(object):

    def product(self, instance):
        if instance.item.content_type.model=='material' and instance.item.content_object.product:
            return instance.item.content_object.product
        elif instance.item.content_type.model=='product':
            return instance.item.content_object
        else:
            return ''
    product.short_description = _("product")
    product.allow_tags = True
    product.is_column = True
    
    def category(self, instance):
        if instance.item.content_type.model=='material' and instance.item.content_object.product:
            return instance.item.content_object.product.category
        elif instance.item.content_type.model=='product':
            return instance.item.content_object.category
        else:
            return ''
    category.short_description = _("Product Category")
    category.allow_tags = True
    category.is_column = True

    def mark(self, instance):
        if instance.item.content_type.model=='material' and instance.item.content_object.mark:
            return instance.item.content_object.mark
        else:
            return ''
    mark.short_description = _("material mark")
    mark.allow_tags = True
    mark.is_column = True

    def qty_format(self, instance):
        if instance.qty == int(instance.qty):
            instance.qty = int(instance.qty)
        return instance.qty
    qty_format.short_description = _("qty")
    qty_format.allow_tags = True
    qty_format.is_column = True

    model_icon = 'cog'
    hidden_menu = False
    active_menu = "storage"
    show_bookmarks = False
    list_display = ('internal_code', 'product', 'category', 'owner', 'furnace_batch', 'mark', 'qty_format', 'unit', 
       'location', 'updated_by',)
    list_display_links = ('internal_code',)
    # list_display_links_details = True

    list_filter = ['journal', 'owner', 'internal_code', 'furnace_batch', 'updated_by', 'qty', 'created_at', 'location']
    search_fields = ['furnace_batch', 'internal_code', 'item__content_type__model']
    actions = [BatchBarcodeAction]
    exclude = ['transport_list_detail']

from django.contrib.contenttypes.models import ContentType
from django.db.models import Count
from device.models import KnifeAttribute
from productcatalog.models import Attribute
class DeviceEntryAdmin(object):

    #by lxy
    def qty_format(self, instance):
        if instance.qty == int(instance.qty):
            instance.qty = int(instance.qty)
        return instance.qty
    qty_format.short_description = _("qty")
    qty_format.allow_tags = True
    qty_format.is_column = True

    def item_name(self, instance):
        item_name = instance.item.content_object.name

        return item_name

    def product_format():
        knife_attributes = KnifeAttribute.objects.values('attribute').annotate(attribute_count=Count('attribute')).order_by('attribute__ext_code')
        attribute_ids = [attribute['attribute'] for attribute in knife_attributes]

        attribute_functions = []
        for attribute_id in attribute_ids:
            function_name = "attribute_%d_function" %(attribute_id)
            generate_function_string = '''
def attribute_%d_function(self, instance):
    attribute_value = instance.item.content_object.knife_attributes.get(attribute_id=%d).value
    return attribute_value
''' %(attribute_id, attribute_id)
            attribute_functions.append([function_name, generate_function_string, attribute_id])

        return attribute_functions


    list_display = ('internal_code', 'item_name', 'usage_time', 'location', 'origin_place','qty_format','updated_by') 
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
        list_display.insert(i+2, function[0])


    item_name.short_description = _("item")
    list_display = tuple(list_display)

    model_icon = 'cog'
    hidden_menu = False
    active_menu = "storage"
    show_bookmarks = False

    list_display_links = ('internal_code', 'item_name')
    # list_display_links_details = True

    list_filter = ['internal_code', 'origin_place', 'usage_time', 'qty', 'location', 'updated_by']
    search_fields = ['internal_code']

    actions = [BatchBarcodeAction]

class ExpenseAdmin(object):

    model_icon = 'cog'
    hidden_menu = False
    active_menu = "storage"
    show_bookmarks = False
    list_display = (
       'date', 'cost', 'prepay'
       )
    list_display_links = ('date',)
    list_display_links_details = True

    list_filter = ['date', 'cost', 'prepay']

    search_fields = ['date']

    aggregate_fields = {'cost': 'sum',}


    data_charts = {
        "user_count": {'title': u"Expense Report", "x-field": "date", "y-field": ('cost'), "order": ('date',)},
    }


class ElectricityChargeAdmin(object):

    def expense_date(self, instance):
        expense_date = ''
        expense_date += str(instance.expense.date)
        return expense_date
    expense_date.short_description = _("expense date")
    expense_date.allow_tags = True
    expense_date.is_column = True
    def expense_cost(self, instance):
        expense_cost = ''
        expense_cost += str(instance.expense.cost)
        return expense_cost
    expense_cost.short_description = _("expense cost")
    expense_cost.allow_tags = True
    expense_cost.is_column = True

    def expense_prepay(self, instance):
        expense_prepay = ''
        expense_prepay += str(instance.expense.prepay)
        return expense_prepay
    expense_prepay.short_description = _("expense prepay")
    expense_prepay.allow_tags = True
    expense_prepay.is_column = True

    model_icon = 'cog'
    hidden_menu = False
    active_menu = "storage"
    show_bookmarks = False
    list_display = (
       'date', 'kilowatt', 'expense_date', 'expense_cost', 'expense_prepay',
       )
    list_display_links = ('date',)
    list_display_links_details = True

    list_filter = ['date', 'kilowatt']

    search_fields = ['date']

    aggregate_fields = {'kilowatt': 'sum',}




    data_charts = {
        "user_count": {'title': _("Electricity Charge Report"), "x-field": "date", "y-field": ('kilowatt'), "order": ('date',)},
        # "per_month": {'title': u"Monthly Users", "x-field": "_chart_month", "y-field": ("cost", 'kilowatt'), 
        #                   "option": {
        #                              "series": {"bars": {"align": "center", "barWidth": 0.8,'show':True}}, 
        #                              "xaxis": {"aggregate": "sum", "mode": "categories"},
        #                              },
        #                 },
    }

    # def _chart_month(self, obj):
    #     return obj.date.strftime("%B")


#by lxy

class TransportListDetailInline(object):
    model = TransportListDetail
    extra = 1
    style = 'table'
    exclude = ['item_entry_code', 'state', 'created_at', 'productionline', 'content_type', 'object_id', 'updated_by']



class TransportListAdmin(object):
    def execute(self, instance):
        if instance.state == 1:
            return "<a href='/warehouse/do_transport/%d/?next=/xadmin/warehouse/transportlist/'>执行</a>" % instance.id
        elif instance.state == 2:
            return "已出库"
        elif instance.state == 5:
            return "已入库"
    execute.short_description = _("execute")
    execute.allow_tags = True
    execute.is_column = True

    def detail_values(self, instance):
        return instance.detail_values
    detail_values.short_description = _("detail_values")
    detail_values.allow_tags = True
    detail_values.is_column = True

    model_icon = 'cog'
    hidden_menu = False
    active_menu = "storage"
    show_bookmarks = False
    list_display = ('list_category', 'transport_category', 'detail_values', 'execute')
    list_display_links = ('list_category', 'transport_category')
    list_display_links_details = True

    list_filter = ['list_category', 'transport_category']
    search_fields = ['internal_code', 'list_category', 'transport_category', 'state', 'created_at', 'productionline', 'updated_by']

    exclude = ['state', 'created_at', 'productionline']

    Inline(TransportListDetail)
    inlines = [TransportListDetailInline]



class TransportListDetailAdmin(object):

    model_icon = 'cog'
    hidden_menu = False
    active_menu = "storage"
    show_bookmarks = False
    list_display = ('item', 'qty', 'unit')
    list_display_links = ('item', 'qty', 'unit')
    list_display_links_details = True

    list_filter = ['item', 'qty', 'unit']
    search_fields = ['item', 'qty', 'unit']




class EntryLogAdmin(object):

    model_icon = 'cog'
    hidden_menu = False
    active_menu = "storage"
    show_bookmarks = False
    list_display = ('item_entry', 'log', 'date_added')
    list_display_links = ('item_entry', 'log', 'date_added')
    list_display_links_details = True

    list_filter = ['item_entry', 'log', 'date_added']
    search_fields = ['item_entry', 'log', 'date_added']



class TransportDetailRecordAdmin(object):

    model_icon = 'cog'
    hidden_menu = False
    active_menu = "storage"
    show_bookmarks = False
    list_display = ('name', 'category', 'norm_code', 'cad_code', 'furnace_batch', 'unit', 
                    'amount', 'note', 'transport_list_number',)
    list_display_links = ('name')
    list_display_links_details = True

    list_filter = ['name', 'category', 'norm_code', 'cad_code', 'furnace_batch', 'unit', 'amount', 'note', 'transport_list_number']
    search_fields = ['name', 'category', 'norm_code', 'cad_code', 'furnace_batch', 'unit', 'amount', 'note', 'transport_list_number']



xadmin.site.register(Location, LocationAdmin)
xadmin.site.register(Item, ItemAdmin)
xadmin.site.register(BomEntry, BomEntryAdmin)
xadmin.site.register(ItemJournal, ItemJournalAdmin)
xadmin.site.register(ItemEntry, ItemEntryAdmin)
xadmin.site.register(DeviceEntry, DeviceEntryAdmin)
xadmin.site.register(Expense, ExpenseAdmin)
xadmin.site.register(ElectricityCharge, ElectricityChargeAdmin)

xadmin.site.register(TransportList, TransportListAdmin)
xadmin.site.register(TransportListDetail, TransportListDetailAdmin)

xadmin.site.register(EntryLog, EntryLogAdmin)
xadmin.site.register(TransportDetailRecord, TransportDetailRecordAdmin)



from django.template import loader
from django.utils.translation import ugettext as _
from xadmin.sites import site
from xadmin.views import BaseAdminPlugin, ListAdminView


class EmptyInventory(BaseAdminPlugin):

    show_or_hidden = (_('show zero item'), _('hide zero item'))

    def block_top_toolbar(self, context, nodes):
        if self.show_or_hidden:
            context.update({
                'show_or_hidden': self.show_or_hidden,
            })
            nodes.append(loader.render_to_string('xadmin/blocks/model_list.top_toolbar.hide_zero_item.html', context_instance=context))


class Inventory_of_warehouse(BaseAdminPlugin):


    def block_nav_menu(self, context, nodes):
        


        context.update({
            
    
        })

        bar = loader.render_to_string('xadmin/blocks/model_list.nav_menu.warehouse_query.html', context_instance=context)

        # nodes.append(bar)

        nodes.insert(0, bar)


class MenuActivePlugin(BaseAdminPlugin):
    active_menu = ""

    # def get_context(self, __):
    #     context = {'l_m_marketing_active': 'active'}
    #     context.update(__())
    #     return context

    def get_context(self, context):
        if self.active_menu == "storage":
            context.update({'l_m_storage_active': 'active'})
        elif self.active_menu == "qa":
            context.update({'l_m_qa_active': 'active'})
        elif self.active_menu == "technology":
            context.update({'l_m_technology_active': 'active'})
        elif self.active_menu == "manufacture":
            context.update({'l_m_manufacture_active': 'active'})
        elif self.active_menu == "marketing":
            context.update({'l_m_marketing_active': 'active'})
        elif self.active_menu == "report":
            context.update({'l_m_report_active': 'active'})
        else:
            pass
        return context

site.register_plugin(MenuActivePlugin, ListAdminView)
site.register_plugin(EmptyInventory, ListAdminView)
site.register_plugin(Inventory_of_warehouse, ListAdminView)

