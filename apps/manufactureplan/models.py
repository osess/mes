#-*- coding:UTF-8 -*-
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings

from yt_object.models import YTObject
from productcatalog.models import Product, Attribute
from customer.models import Customer
from technologies.models import Technology,OperationGroup,Operation,OperationAttribute

from person.models import Employee
from warehouse.models import  DeviceEntry, BomEntry

from yt_log.models import StateDetail
from workflows.utils import ContentType,get_workflow,WorkflowObjectRelation,get_state
# from django.db.models import Q
# import constant
from django.utils.log import logger


__all__ = [
    'Order',
    'ProductItem',
    'ManufacturePlan',
    'ProductionLine',
    'OperationGroupRecord',
    'OperationRecord',
    'ManufactureItemGroup',
    'ManufactureItem',
    'ManufactureRecord',
    'ManufactureRelation',
    'QARecord',
    'QARecordAttribute',
    'RejectProductRecord',
]

#from extensions.custom_fields.datetime_format import ConvertingDateTimeFeild

CHOICE_QA_EXCESSIVE_STATUS = (
    (1, _("normal")),                 #正常，默认的状态
    (2, _("excessive")),              #出错，当产品出错且未处理时，置此状态
    (3, _("passed")),                 #原状态，表示通过，只有QARecordAttribute可以置此状态
    (4, _("no_passed")),              #原状态，表示不通过，只有QARecordAttribute可以置此状态
    (5, _("passed_excessive")),       #非原状态，至少有一个未处理状态，不得包含未通过状态
    (6, _("no_passed_excessive")),    #非原状态，至少有一个未处理状态，至少有一个未通过状态
    (7, _("passed_decided")),         #非原状态，不得包含未处理状态，不得包含未通过状态
    (8, _("no_passed_decided")),      #非原状态，不得包含未处理状态，至少有一个未通过状态
)

CHOICE_STATUS_STATE = (
    (1, _("Normal")),                    # 正常
    (2, _("Invalid")),                   # 作废
    (3, _("Old Rev")),                   # 老版本
)

class Order(models.Model):
#-------------------------------------------------------------------------------
    """
    订单 -- Order

    **字段**
    contract_code  合同编号
    customer       客户
    order_time     下单日期
    status         订单状态 : 正常/作废/老版本
    """
    contract_code = models.CharField(max_length=255, verbose_name=_("contract_code"))
    #name          = models.CharField(max_length=255, verbose_name=_("order name"))
    customer      = models.ForeignKey(Customer, related_name="orders", verbose_name=_("customer"))
    order_time    = models.DateTimeField(verbose_name=_("order_time"))
    
    status        = models.PositiveSmallIntegerField(choices=CHOICE_STATUS_STATE, default=1, verbose_name=_("status"))

    def __unicode__(self):

        return "%s" %(self.contract_code)

    class Meta:
        verbose_name = _('Order')
        verbose_name_plural = _('Orders')
        ordering = ('-order_time',)

#-------------------------------------------------------------------------------
    @property
    def name(self):
        return self.contract_code

    @property
    def code(self):
        return self.contract_code

    @property
    def is_status_normal(self):
        ''' 是否是正常状态 '''
        return self.status == 1
    @property
    def is_status_invalid(self):
        ''' 是否是无效状态 '''
        return self.status == 2
    @property
    def is_status_old(self):
        ''' 是否是老版本 '''
        return self.status == 3

class ProductItem(models.Model):
    """
    产品实例

    **字段**
    order          订单
    product        产品
    quantity       数量
    finish_time    交货日期
    unit_price     单价
    """
    order       = models.ForeignKey(Order, related_name="product_items", verbose_name=_("order"))
    product     = models.ForeignKey(Product, related_name="product_items", verbose_name=_("product"))
    quantity    = models.IntegerField(max_length=255, verbose_name=_("product quantity"))
    finish_time = models.DateTimeField(verbose_name=_("product_item_finish_time"))
    unit_price  = models.FloatField(blank=True, null=True, verbose_name=_("unit_price"))

    def __unicode__(self):
        return "%s" %(self.product.name)

    class Meta:
        verbose_name = _('ProductItems')
        verbose_name_plural = _('ProductItems')
        ordering = ('-product',)


class ManufacturePlan(YTObject):
    """
    生产通知单

    **字段**
    name            生产通知单名称
    order           订单
    start_time      下单时间
    status          状态
    """
    name        = models.CharField(max_length=255, verbose_name=_("manufacture plan name"))
    order       = models.ForeignKey(Order, related_name="manufacture_plan", verbose_name=_("manufacture_plan order"))
    start_time  = models.DateTimeField(verbose_name=_("manufacture_plan_start_time"))
    #finish_time = models.DateTimeField(verbose_name=_("finish_time"))
    
    status        = models.PositiveSmallIntegerField(choices=CHOICE_STATUS_STATE, default=1, verbose_name=_("status"))

    def __unicode__(self):
        cad_codes = ''
        for manu_item_group in self.manu_item_groups.all():
            cad_codes += ' | '
            cad_codes += manu_item_group.product.cad_code
        return "%s:%s" %(self.name, cad_codes)

    class Meta:
        verbose_name = _('ManufacturePlans')
        verbose_name_plural = _('ManufacturePlans')
        ordering = ('-date_added',)
        # permissions = (
        #     ("start_manufactureplan_workflow", "Can Start Manufactureplan Workflow"),
        #     ("show_manufactureplan_workflow", "Can Show Manufactureplan Workflow"),
        # )
#-------------------------------------------------------------------------------
    @property
    def is_status_normal(self):
        ''' 是否是正常状态 '''
        return self.status == 1
    @property
    def is_status_invalid(self):
        ''' 是否是无效状态 '''
        return self.status == 2
    @property
    def is_status_old(self):
        ''' 是否是老版本 '''
        return self.status == 3

    #TODO
    @property
    def item_entries_ok(self):
        manu_item_groups = self.manu_item_groups.exclude(productionline=None)
        if manu_item_groups and manu_item_groups[0].productionline:
            for oper_group_record in manu_item_groups[0].productionline.oper_group_records.all():
                if not oper_group_record.device_items.count():
                    return False
            return True
        else:
            return False

    @property
    def is_item_entries_ready(self):
        manu_item_groups = self.manu_item_groups.exclude(productionline=None)
        for manu_item_group in manu_item_groups:
            if not manu_item_group.is_item_entries_ready:
                return False
        return True

    @property
    def technology_ok(self):
        bool_tag = True
        for manu_item_group in self.manu_item_groups.all():
            technology = manu_item_group.technology
            if not technology or technology.technology_workflow_status != 2:
                bool_tag =  False
                break
        return bool_tag

    @property
    def manufactureplan_workflow_status(self):
        workflow = get_workflow(self)
        if workflow:
            current_state = get_state(self)
            if current_state.transitions.all():
                return 1#started
            else:
                return 2#finished
        else:
            return 0#wait for start
            
    @property
    def manufactureplan_workflow_approved(self):
        workflow = get_workflow(self)
        if workflow:
            workflow_object_relation = WorkflowObjectRelation.objects.get(
                content_type = ContentType.objects.get_for_model(self),
                content_id   = self.id,
                workflow     = workflow
            )
            workflow_logs = []
            for state_detail in workflow_object_relation.state_details.all():
                workflow_logs.extend(state_detail.workflow_logs.all())
            workflow_logs.sort(key=lambda k: k.date_added, reverse=True)
            if workflow_logs:
                if workflow_logs[0].type == 1:
                    return True
                else:
                    return False
            else:
                return True

    @property
    def state_detail(self):
        technology_type = ContentType.objects.get_for_model(self)
        workflow_object_relation = WorkflowObjectRelation.objects.get(content_type__pk=technology_type.id,content_id=self.id)
        current_state = get_state(self)
        state_detail = StateDetail.objects.get(workflow_object_relation=workflow_object_relation,state=current_state)
        return state_detail
    
    @property
    def workflow_object_relation(self):
        technology_type = ContentType.objects.get_for_model(self)
        workflow_object_relation = WorkflowObjectRelation.objects.get(content_type__pk=technology_type.id,content_id=self.id)
        return workflow_object_relation

    @property
    def productionlines(self):
        productionlines = []
        for manu_item_group in self.manu_item_groups.all():
            if manu_item_group.productionline:
                productionlines.append(manu_item_group.productionline)
        return productionlines

    @property
    def first_productionline(self):
        if self.productionlines:
            return self.productionlines[0]

    @property
    def has_materials(self):
        for manu_item_group in self.manu_item_groups.all():
            bom_entries = BomEntry.objects.filter(
                productionline = manu_item_group.productionline,
                bom_category   = 1,
            )
            if bom_entries and bom_entries[0].state == 2:
                return True
        return False

    @property
    def waiting_materials(self):#applyed but not ok
        for manu_item_group in self.manu_item_groups.all():
            bom_entries = BomEntry.objects.filter(
                productionline = manu_item_group.productionline,
                bom_category   = 1,
            )
            if bom_entries and bom_entries[0].state != 2:
                return True
        return False

    def save(self, *args, **kwargs):
        if not self.code:
            count = ManufacturePlan.objects.all().count()
            self.code = 'MP-%03d' %(count+1,)
        if not self.name:
            self.name = self.order.name + '生产通知单'
        super(self.__class__, self).save(*args, ** kwargs)

CHOICE_PRODUCTIONLINE_STATE = (
    (1, _("waiting")),
    # (10, _("applying materials")),#正在申领所需物品
    # (11, _("assigning materials")),#正在分配所需物品
    # (12, _("assign materials ok")),#所需物品分配成功
    (2, _("Working")),
    (3, _("Finished")),
    (4, _("Error")),
    (5, _("record_pass")),
    (6, _("Reworking")),
)
CHOICE_LOCATION_STATUS = (
    (1, _("waiting")),
    (2, _("Working")),
    (3, _("Finished")),
    (4, _("Error")),
)
from warehouse.models import TransportList
class ProductionLine(models.Model):
    '''
    生产任务

    **字段**
    technology                  工艺
    state                       状态
    current_operation_record    当前工步
    location_status             状态
    date_added                  创建日期
    '''
    #code 发放号三位
    #name        = models.CharField(max_length=255, unique=False, verbose_name=_("production line name"))
    technology  = models.ForeignKey(Technology, unique=False, related_name="production_lines", verbose_name=_("technology"))
    state       = models.PositiveSmallIntegerField(choices=CHOICE_PRODUCTIONLINE_STATE, default=1, verbose_name=_("production line state"))
    date_added  = models.DateTimeField(auto_now_add=True, verbose_name=_("date_added"))
    
    current_operation_record = models.ForeignKey('OperationRecord', related_name="production_line", verbose_name=_("current_operation_record"))
    
    location_status = models.PositiveSmallIntegerField(choices=CHOICE_LOCATION_STATUS, default=1, verbose_name=_("location status"))
    
    #start_time  = models.DateTimeField(unique=False, blank=True, null=True, verbose_name=_("start_time"))
    #finish_time = models.DateTimeField(unique=False, blank=True, null=True, verbose_name=_("finish_time"))
    
    # TODO:暂时不加，待客户确定
    # workblank_item = models.ForeignKey(ItemEntry, blank=True, null=True, related_name="production_line", verbose_name=_("workblank_item"))
    # material_items = models.ManyToManyField(ItemEntry, blank=True, null=True, related_name="production_line", verbose_name=_("material_items"))

    def __unicode__(self):
        #return self.technology.name
        return "%s-%s-%d" %(self.technology.name, self.date_added.strftime("%y%m%d"), self.id)

    class Meta:
        verbose_name = _('ProductionLine')
        verbose_name_plural = _('ProductionLines')
        ordering = ('-date_added',)
        permissions = (
            ("monitor_productionLine", "Can Monitor ProductionLine"),
        )

#-------------------------------------------------------------------------------
    @property
    def is_show_in_operating_platform(self):
        ''' 是否在工作台显示 '''
        # 1. 已经结束了的，不显示
        if self.is_state_finished:
            return False
        if self.location_status == 3:           # finished
            return False
        # 2. 生产通知单存在且状态正常
        if self.manu_item_group and self.manu_item_group.manufactureplan and \
        self.manu_item_group.manufactureplan.is_status_normal:
            return True
        return False

    @property
    def is_batch_handle_allowed(self):
        '''
        是否允许批量处理 
        如果当前工件的状态在允许批量处理的范围内，就允许批量处理
        '''
        if not self.can_import:
            return False

        mi_list = []
        for mi in self.self_manufacture_items:
            if mi.qa_excessive_status == 2:
                mi_list.append(mi)
        if len(mi_list) == len(self.self_manufacture_items):
            return False

        from .utils import get_all_batch_handle_productionlines
        logger.info(get_all_batch_handle_productionlines())
        if self.id in get_all_batch_handle_productionlines():
            # 如果在批量处理列表中，就允许 批量操作
            return True
        return False


    @property
    def is_state_waiting(self):
        return self.state == 1
    @property
    def is_state_working(self):
        return self.state == 2
    @property
    def is_state_finished(self):
        return self.state == 3
    @property
    def is_state_error(self):
        return self.state == 4
    @property
    def is_state_record_pass(self):
        return self.state == 5
    @property
    def is_state_reworking(self):
        return self.state == 6

    def set_state_waiting(self,*args,**kwargs):
        self.state = 1
        super(ProductionLine, self).save(*args, **kwargs)
    def set_state_working(self,*args,**kwargs):
        self.state = 2
        super(ProductionLine, self).save(*args, **kwargs)
    def set_state_finished(self,*args,**kwargs):
        self.state = 3
        super(ProductionLine, self).save(*args, **kwargs)
    def set_state_error(self,*args,**kwargs):
        self.state = 4
        super(ProductionLine, self).save(*args, **kwargs)
    def set_state_record_pass(self,*args,**kwargs):
        self.state = 5
        super(ProductionLine, self).save(*args, **kwargs)
    def set_state_reworking(self,*args,**kwargs):
        self.state = 6
        super(ProductionLine, self).save(*args, **kwargs)


    @property 
    def is_item(self):
        if self.manufacture_items.all():
            return True
        return False
    @property
    def code(self):
        return self.technology.product.cad_code

    @property
    def name(self):
        return self.technology.name

    @property
    def manu_item_group(self):
        for manu_item_group in self.manu_item_groups.all():
            return manu_item_group

    @property
    def item_entries_ok(self):
        if self.has_devices and self.manu_item_group.is_item_entries_ready:
            return True
        else:
            return False

    @property
    def parent_productionline(self):
        for manufacture_item in self.manufacture_items.all():
            return manufacture_item.manu_item_group.productionline

    @property
    def children_productionlines(self):
        mig = self.manu_item_group
        return [mi.productionline for mi in mig.manufacture_items.all()] if mig else []

    @property
    def first_child_productionline(self):
        pls = self.children_productionlines
        return pls[0] if pls else self

    @property
    def current_state_percent(self):
        current_operation = self.current_operation_record.operation
        full_operations   = []
        done_operations   = []
        operation_groups  = [record.operation_group for record in self.oper_group_records.all().order_by('operation_group__order')]
        for operation_group in operation_groups:
            operations = operation_group.operations.all().order_by('order')
            if operation_group.order < current_operation.operation_group.order:
                done_operations.extend(operations)
            elif operation_group.order == current_operation.operation_group.order:
                for operation in operations:
                    if operation.order <= current_operation.order:
                        done_operations.append(operation)
            full_operations.extend(operations)
        return 100*len(done_operations)//len(full_operations)

    @property
    def first_operation_record(self):
        '''
        第一个工步记录
        '''
        state = get_workflow(self).initial_state
        for oper_group_record in self.oper_group_records.all():
            for operation_record in oper_group_record.operation_records.all():
                if operation_record.operation.state == state:
                    return operation_record

    @property
    def is_not_ready(self):
        if get_workflow(self.manufactureplan):
            if not self.item_entries_ok:
                return True
            else:
                return False
            if get_workflow(self):
                return False
        else:
            return True

    @property
    def is_waiting(self):
        if get_workflow(self.manufactureplan):
            if self.item_entries_ok:
                return True
            else:
                return False
            if get_workflow(self):
                return False
            else:
                return True
        else:
            return False

    @property
    def is_working(self):
        if get_workflow(self) and self.state != 3:
            return True
        else:
            return False

    @property
    def is_finished(self):
        if self.state == 3:
            return True
        else:
            return False
    # #replaced by column location_status
    # @property
    # def location_status(self):
    #     transport_lists_in = self.transport_lists.filter(list_category=1,transport_category=2).order_by('-created_at')
    #     transport_lists_out = self.transport_lists.filter(list_category=1,transport_category=1).order_by('-created_at')
    #     if not transport_lists_in:
    #         return 1
    #     elif not transport_lists_out:
    #         if all(transport_list.state != 1 for transport_list in transport_lists_in):
    #             return 3
    #         else:
    #             return 2
    #     elif len(transport_lists_in) == len(transport_lists_out):
    #         if all(transport_list.state != 1 for transport_list in transport_lists_out):
    #             return 1
    #         else:
    #             return 4
    #     elif len(transport_lists_in) > len(transport_lists_out):
    #         if all(transport_list.state != 1 for transport_list in transport_lists_in):
    #             return 3
    #         else:
    #             return 2
    #     else:
    #         return 0

    @property
    def can_import(self):
        if self.location_status == 1:
            return True
        else:
            return False

    @property
    def is_importing(self):
        if self.location_status == 2:
            return True
        else:
            return False

    @property
    def can_export(self):
        if self.location_status == 3:
            return True
        else:
            return False

    @property
    def is_exporting(self):
        if self.location_status == 4:
            return True
        else:
            return False

    @property
    def has_devices(self):
        for oper_group_record in self.oper_group_records.all():
            #   不需要设备                                     # 已分配设备
            if not oper_group_record.operation_group.device or oper_group_record.device_items.count():
                pass
            else:
                return False
        return True

    @property
    def waiting_devices(self):#applyed but not ok
        if not self.has_devices:
            transports_list = TransportList.objects.filter(
                list_category      = 2,#Device
                transport_category = 1,#Output
                state              = 1,#Waitting
                productionline     = self,
            )
            if transports_list:
                return True
        return False
    #TODO
    @property
    def devices_export_list_id(self):
        transport_list = TransportList.objects.get(
            list_category = 2,
            transport_category = 1,
            productionline = self
        )
        if transport_list:
            return transport_list.id

    @property
    def has_knifes(self):
        for oper_group_record in self.oper_group_records.all():
            for operation_record in oper_group_record.operation_records.all():
                if operation_record.knife_items.all():
                    return True
        return False

    @property
    def waiting_knifes(self):#applyed but not ok
        if not self.has_knifes:
            transports_list = TransportList.objects.filter(
                list_category      = 3,#Knife
                transport_category = 1,#Output
                state              = 1,#Waitting
                productionline_id  = self.id,
            )
            if transports_list:
                return True
        return False
    #TODO
    @property
    def knifes_export_list_id(self):
        transport_list = TransportList.objects.get(
            list_category = 3,
            transport_category = 1,
            productionline = self
        )
        if transport_list:
            return transport_list.id

    @property
    def has_tools(self):
        for oper_group_record in self.oper_group_records.all():
            for operation_record in oper_group_record.operation_records.all():
                if operation_record.tool_items.all():
                    return True
        return False

    @property
    def waiting_tools(self):#applyed but not ok
        if not self.has_tools:
            transports_list = TransportList.objects.filter(
                list_category      = 4,#Tool
                transport_category = 1,#Output
                state              = 1,#Waitting
                productionline     = self,
            )
            if transports_list:
                return True
        return False
    #TODO
    @property
    def tools_export_list_id(self):
        transport_list = TransportList.objects.get(
            list_category = 4,
            transport_category = 1,
            productionline = self
        )
        if transport_list:
            return transport_list.id



    # @property
    # def current_operation_record(self):
    #     from workflows.utils import get_state
    #     current_state = get_state(self)
    #     current_operation_record = None
    #     for operation_group_record in self.oper_group_records.all():
    #         for operation_record in operation_group_record.operation_records.all():
    #             if operation_record.operation.state == current_state:
    #                 current_operation_record = operation_record
    #     return current_operation_record

    @property
    def manufactureplan(self):
        for manu_item_group in self.manu_item_groups.all():
            return manu_item_group.manufactureplan
    
    @property
    def product(self):
        if self.is_item:
            for manufacture_item in self.manufacture_items.all():
                return manufacture_item.manu_item_group.product
        else:
            for manu_item_group in self.manu_item_groups.all():
                return manu_item_group.product

    @property
    def self_manufacture_items(self):
        manufacture_items = []
        for manu_item_group in self.manu_item_groups.all():
            for manufacture_item in manu_item_group.manufacture_items.all():
                manufacture_items.append(manufacture_item)
        return manufacture_items

    @property
    def no_no_passed_manufacture_items(self):
        manufacture_passed_items = []
        for manufacture_item in self.self_manufacture_items:
            if manufacture_item.current_qa_records_no_no_passed:
                manufacture_passed_items.append(manufacture_item)
        return manufacture_passed_items
    
    @property
    def no_excessive_manufacture_items(self):
        manufacture_passed_items = []
        for manufacture_item in self.self_manufacture_items:
            if not manufacture_item.excessive:
                manufacture_passed_items.append(manufacture_item)
        return manufacture_passed_items

    #by lxy
    @property
    def manufactureplan_output_status(self):
        output_status_list = []
        for bom in self.boms.filter(bom_category = 1):
            output_status_list.append(bom.state)

        waitting = 1
        already_output = 2
        insufficient = 3
        error = 4
        # already_import = 5
        if ((waitting not in output_status_list) and 
            (insufficient not in output_status_list) and 
            (error not in output_status_list)):
            return 'all_output'
        elif already_output not in output_status_list:
            return 'waitting'
        else:
            return 'some_bom_output'

    @property
    def manufactureplan_import_status(self):
        import_status_list = []
        for bom in self.boms.filter(bom_category = 2):
            import_status_list.append(bom.state)

        waitting = 1
        already_import = 5
        if waitting not in import_status_list:
            return 'all_import'
        elif already_import not in import_status_list:
            return 'waitting'
        else:
            return 'some_bom_import'


class OperationGroupRecord(models.Model):
    '''
    工序记录
    '''
    #code 附加发放号后三位
    productionline  = models.ForeignKey(ProductionLine, related_name="oper_group_records", verbose_name=_("productionline"))
    operation_group = models.ForeignKey(OperationGroup, related_name="oper_group_records", verbose_name=_("operation_group"))
    device_items    = models.ManyToManyField(DeviceEntry, blank=True, null=True, related_name="oper_group_record", verbose_name=_("device_items"))
    #job             = models.ForeignKey(Job, blank=True, null=True, related_name="oper_group_record", verbose_name=_("job"))
    #device_entry    = models.ForeignKey(DeviceEntry, blank=True, null=True, verbose_name=_("device_items"))
    

    def __unicode__(self):

        return self.operation_group.name

    class Meta:
        verbose_name = _('OperationGroupRecords')
        verbose_name_plural = _('OperationGroupRecords')
        ordering = ('operation_group__order',)

    @property 
    def can_applied_device_items(self):
        device       = self.operation_group.device
        # 如果不需要设备,则跳过
        if device is None:
            return DeviceEntry.objects.none()

        if device.id == 0:
            device_items = DeviceEntry.objects.filter(internal_code__icontains="KCSK").order_by('id')
        else:
            content_type = ContentType.objects.get_for_model(device)
            device_items = DeviceEntry.objects.filter(
                item__content_type_id = content_type.id,
                item__object_id       = device.id,
            ).order_by('id')

        return device_items

    #lxy
    @property 
    def last_operation_record(self):
        for operation_record in self.operation_records.all().order_by('-operation__order'):
            return operation_record

CHOICE_STATE_STATUS = (
    (1, _("Waiting")),
    (2, _("Working")),
    (3, _("QASelfRecord")),
    (4, _("QADoubleRecord")),    # 互检
    (5, _("QAInspectorRecord")), # 检验
    (6, _("Finished")),
    (7, _("Error")),
    (8, _("Reworking")),
)

color_name = {
    1:"",
    2:"lava",
    3:"sky",
    4:"sky",
    5:"sky",
    6:"vine",
    7:"industrial",
    8:"social",
}

QUALITY_STATUS = (
    (0,_("untreated")),   # 未处理
    (1,_("passed")),   # 合格
    (2,_("no_passed")), # 不合格
)

class OperationRecord(models.Model):
    '''
    OperationRecord - 工步记录 

    **字段**
    oper_group_record     工序记录
    operation             工步
    status                状态
    qa_excessive_status   问题
    knife_items           刀具
    tool_items            工具
    quantity              数量
    '''

    #code
    #employee            = models.ForeignKey(Employee, blank=True, null=True, related_name="operation_records", verbose_name=_("employee"))
    oper_group_record   = models.ForeignKey(OperationGroupRecord, related_name="operation_records", verbose_name=_("oper_group_record"))
    operation           = models.ForeignKey(Operation, related_name="operation_records", verbose_name=_("operation"))
    status              = models.PositiveSmallIntegerField(choices=CHOICE_STATE_STATUS, default=1, verbose_name=_("status"))
    qa_excessive_status = models.PositiveSmallIntegerField(choices=CHOICE_QA_EXCESSIVE_STATUS, default=1, verbose_name=_("qa_excessive_status"))
    knife_items         = models.ManyToManyField(DeviceEntry, blank=True, null=True, related_name="knife_operation_record", verbose_name=_("knife_items"))
    tool_items          = models.ManyToManyField(DeviceEntry, blank=True, null=True, related_name="tool_operation_record", verbose_name=_("tool_items"))

    quantity             = models.IntegerField(max_length=255, default=1, verbose_name=_("quantity"))
    #检验人

    # by recall
    temp_batch_note     = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("temp batch note"))
    temp_batch_ts       = models.DateTimeField(blank=True, null=True, verbose_name=_("temp batch timestamp"))
    temp_batch_operator = models.ForeignKey(User,blank=True,null=True, verbose_name= _("temp batch operator"))
    quality_status     = models.IntegerField(choices=QUALITY_STATUS,default=0,verbose_name=_("quality status"))

    def __unicode__(self):

        return self.operation.name

    class Meta:
        verbose_name = _('OperationRecord')
        verbose_name_plural = _('OperationRecords')
        ordering = ('operation__order',)

#-------------------------------------------------------------------------------
    @property
    def is_quality_status_untreated(self):
        ''' 未处理 '''
        return self.quality_status == 0
    @property
    def is_quality_status_passed(self):
        ''' 合格 '''
        return self.quality_status == 1
    @property
    def is_quality_status_no_passed(self):
        '''不合格'''
        return self.quality_status == 2

    @property
    def is_status_waiting(self):
        return self.status == 1
    @property
    def is_status_working(self):
        return self.status == 2
    @property
    def is_status_qa_self_record(self):
        ''' 自检 '''
        return self.status == 3
    @property
    def is_status_qa_double_record(self):
        ''' 互检 '''
        return self.status == 4
    @property
    def is_status_qa_inspector_record(self):
        ''' 检验 '''
        return self.status == 5
    @property
    def is_status_finished(self):
        return self.status == 6
    @property
    def is_status_error(self):
        return self.status == 7
    @property
    def is_status_reworking(self):
        return self.status == 8

    @property
    def order_code(self):
        return "%03d%03d" %(self.operation.operation_group.order,self.operation.order)

    @property
    def parent_operation_record(self):
        pl = self.oper_group_record.productionline
        parent_pl = pl.parent_productionline
        for oper_group_record in parent_pl.oper_group_records.all():
            for operation_record in oper_group_record.operation_records.all():
                if operation_record.operation == self.operation:
                    return operation_record
        
    @property
    def all_manufacture_items_count(self):
        # import pdb; pdb.set_trace()
        migs = self.oper_group_record.productionline.manu_item_groups.all()
        if migs:
            # pl = self.oper_group_record.productionline
            n = 0
            for mig in migs:
                n += mig.manufacture_items.count()
            return n
        else:
            return None

    @property
    def self_manufacture_items_count(self):
        # import pdb; pdb.set_trace()
        migs = self.oper_group_record.productionline.manu_item_groups.all()
        if migs:
            pl = self.oper_group_record.productionline
            mis = ManufactureItem.objects.filter(
                manu_item_group__productionline=pl,
                productionline__current_operation_record__operation=self.operation
            ).count()
            return mis
        else:
            return None

    #by lxy
    @property
    def qa_first_self(self):
        for qa in self.self_records.all().order_by('id'):
            if qa.type == 1:
                return qa

    #by lxy
    @property
    def qa_first_double(self):
        for qa in self.self_records.all().order_by('id'):
            if qa.type == 2:
                return qa

    #by lxy
    @property
    def qa_first_inspector(self):
        for qa in self.self_records.all().order_by('id'):
            if qa.type == 3:
                return qa

    @property
    def QA_status(self):
        status = 7
        for manu_item_group in self.oper_group_record.productionline.manu_item_groups.all():
            for manufacture_item in manu_item_group.no_excessive_manufacture_items:
                if status > manufacture_item.status:
                    status = manufacture_item.status

        self.status = status
        self.save()
        return self.status
        


class ManufactureItemGroup(models.Model):
    """
    生产任务  MIG

    **字段**
    product                 产品
    quantity                数量
    productionline          生产任务
    manufactureplan         生产通知单
    qa_excessive_status     问题
    batch_code              批次号
    is_batch                是否是批量
    is_item_entries_ready   物品是否准备好
    finish_time             完成日期
    task_code               任务编号
    furnace_batch           炉批号
    """
    product              = models.ForeignKey(Product, related_name="manu_item_groups", verbose_name=_("product"))
    quantity             = models.IntegerField(max_length=255, verbose_name=_("quantity"))
    productionline       = models.ForeignKey(ProductionLine, blank=True, null=True, related_name="manu_item_groups", verbose_name=_("productionline"))
    manufactureplan      = models.ForeignKey(ManufacturePlan, related_name="manu_item_groups", verbose_name=_("manufacture_plan"))
    qa_excessive_status  = models.PositiveSmallIntegerField(choices=CHOICE_QA_EXCESSIVE_STATUS, default=1, verbose_name=_("qa_excessive_status"))
    batch_code           = models.CharField(max_length=20, blank=True, null=True, verbose_name=_("batch_code"))
    is_batch             = models.BooleanField(default=False, verbose_name=_("is_batch"))

    is_item_entries_ready = models.BooleanField(default=False, verbose_name=_("is_item_entries_ready"))
    finish_time          = models.DateTimeField(blank=True, null=True, verbose_name=_("MIG_finish_time"))
    
    task_code       = models.CharField(max_length=125, blank=True, null=True, verbose_name=_("task code"))
    furnace_batch   = models.CharField(max_length=125, blank=True, null=True, verbose_name=_("furnace batch"))
    
    def __unicode__(self):
        return "id:%d-%s(%s)" %(self.id, self.product.name, self.quantity)

    class Meta:
        verbose_name = _('ManufactureItemGroup')
        verbose_name_plural = _('ManufactureItemGroups')
        ordering = ('manufactureplan',)

    @property
    def code(self):
        return self.product.cad_code

    @property
    def name(self):
        return self.product.name

    @property
    def technology(self):
        if self.productionline:
            technology = self.productionline.technology
        else:
            technologies = Technology.objects.filter(product=self.product)
            technologies_list = list(technologies)
            technologies_list.sort(key=lambda k: (k.rev_order,), reverse=True)
            technology = technologies_list[0] if technologies_list else None
        return technology
            
    @property
    def item_entries_ok(self):
        if self.productionline.has_devices and self.is_item_entries_ready:
            return True
        else:
            return False

    @property
    def current_state_percent(self):
        percents = [m.current_state_percent for m in self.manufacture_items.all()]
        return reduce(lambda x,y:x+y,percents) / len(percents)

    @property
    def current_manufacture_items_decided(self):
        decided_tag = True
        for manufacture_item in self.manufacture_items.all():
            if not manufacture_item.current_qa_records_decided:
                decided_tag = False
                break
        return decided_tag

    @property
    def current_manufacture_items_passed(self):
        passed_tag = True
        for manufacture_item in self.manufacture_items.all():
            if not manufacture_item.current_qa_records_passed:
                passed_tag = False
                break
        return passed_tag

    @property
    def current_manufacture_items_no_passed(self):
        passed_tag = False
        for manufacture_item in self.manufacture_items.all():
            if manufacture_item.current_qa_records_no_passed:
                passed_tag = True
                break
        return passed_tag

    @property
    def no_no_passed_manufacture_items(self):
        passed_manufacture_items = []
        for manufacture_item in self.manufacture_items.all():
            if manufacture_item.current_qa_records_no_no_passed:
                passed_manufacture_items.append(manufacture_item)
        return passed_manufacture_items

    @property
    def no_excessive_manufacture_items(self):
        items = [item for item in self.manufacture_items.all() if not item.excessive]
        return items

    @property
    def excessive(self):
        if self.qa_excessive_status == 1:
            return False
        else:
            return True

    @property
    def current_excessive(self):
        for manufacture_item in self.no_excessive_manufacture_items:
            if manufacture_item.qa_excessive_status != 1:
                return True
                break
        return False

    @property
    def QA_status(self):
        return self.productionline.current_operation_record.QA_status

class ManufactureItem(YTObject):
    '''
    工件 MI

    **字段**
    manu_item_group         生产任务
    productionline          生产任务
    status                  状态
    qa_excessive_status     问题
    batch_code              批次号
    '''
    manu_item_group      = models.ForeignKey(ManufactureItemGroup, related_name="manufacture_items", verbose_name=_("manu_item_group"))
    productionline       = models.ForeignKey(ProductionLine, blank=True, null=True, related_name="manufacture_items", verbose_name=_("productionline"))
    status               = models.PositiveSmallIntegerField(choices=CHOICE_STATE_STATUS, default=1, verbose_name=_("manufacture item status"))
    qa_excessive_status  = models.PositiveSmallIntegerField(choices=CHOICE_QA_EXCESSIVE_STATUS, default=1, verbose_name=_("qa_excessive_status"))
    batch_code           = models.CharField(max_length=20, blank=True, null=True, verbose_name=_("batch_code"))
    
    def __unicode__(self):
        return "%s:%s" %(self.manu_item_group.product.name, self.code)

    class Meta:
        verbose_name = _('ManufactureItem')
        verbose_name_plural = _('ManufactureItems')
        ordering = ('id',)
        permissions = (
            ("quality_dispaly", "Quality Dispaly"),
            ("quality_manufactureitem", "Quality ManufactureItem"),
        )

#-------------------------------------------------------------------------------
    @property
    def get_all_qa_self_record(self):
        ''' 返回所有自检记录 '''
        return self.self_records.all().filter(type=1)

    @property
    def get_all_qa_double_check_record(self):
        ''' 返回所有互检记录 '''
        return self.self_records.all().filter(type=2)

    @property
    def is_new_check_flow_qa_self_item_wait(self):
        ''' 自检等待 '''
        # 如果自检记录有需要质量部确认的，则进入等待状态
        if self.self_records.all().filter(qa_excessive_status=2,type=1).exists():
            return True
        else:
            return False
    @property
    def is_new_check_flow_qa_double_item_wait(self):
        ''' 互检等待 '''
        if self.self_records.all().filter(qa_excessive_status=2,type=2).exists():
            return True
        else:
            return False
    @property
    def num_of_operation_group(self):
        ''' 工序总数量 '''
        technology = self.current_operation_record.operation.operation_group.technology
        return OperationGroup.objects.filter(technology=technology).count()
    @property
    def num_of_current_operation(self):
        ''' 当前工步的数量 '''
        operation_group = self.current_operation_record.operation.operation_group
        return Operation.objects.filter(operation_group=operation_group).count()
    @property
    def is_current_operation_group_final_check(self):
        ''' 当前工序是终检 '''
        return self.current_operation_record.operation.operation_group.name == u'终检'

    @property
    def is_manufacture_records_exists(self):
        '''
        工件的当前工步是否存在生产记录
        '''
        return ManufactureRecord.objects.filter(
                    manufacture_item=self,
                    operation_record=self.current_operation_record)\
                .exists()

    @property
    def name(self):
        return self.manu_item_group.product.name

    @property
    def is_batch(self):
        return self.manu_item_group.is_batch

    @property
    def qty(self):
        if self.is_batch:
            return self.manu_item_group.quantity
        else:
            return 1

    @property
    def reject_product_records(self):
        reject_product_records = []
        for qa_record in self.self_records.all():
            reject_product_records.extend(qa_record.reject_product_record.all())
        return reject_product_records

    @property
    def worked_hours(self):
        from datetime import timedelta
        from yt_timesheet.models import Timesheet
        worked_hours = timedelta(0,0,0)
        for manufacture_record in self.manufacture_records.all():
            content_type = ContentType.objects.get_for_model(manufacture_record)
            timesheets = Timesheet.objects.filter(content_type__pk=content_type.id,object_id=manufacture_record.id)
            worked_hour = sum([timesheet.difference_hours for timesheet in timesheets],timedelta())
            worked_hours += worked_hour
        return worked_hours

    @property
    def holderjs_color_name(self):
        return color_name[self.status]

    @property
    def current_state_percent(self):
        current_operation_group = self.current_operation_record.operation.operation_group
        operation_groups  = self.productionline.technology.operation_groups.all().order_by('order')
        return 100*current_operation_group.order//len(operation_groups)

    @property
    def current_operation_group_percent(self):
        current_operation_group = self.current_operation_record.operation.operation_group
        operation_groups  = self.productionline.technology.operation_groups.all().order_by('order')
        return "%d|%d" % (current_operation_group.order,len(operation_groups))

    @property
    def current_operation_record(self):
        return self.productionline.current_operation_record

    @property
    def excessive_qa_record(self):
        qa_records = self.self_records.exclude(qa_excessive_status=1)
        if qa_records:
            return qa_records[0]

    @property
    def current_qa_records(self):
        qa_records = self.self_records.filter(
            operation_record=self.current_operation_record,
        ).order_by('type')
        return qa_records

    @property
    def current_qa_record(self):
        qa_records = self.current_qa_records
        if qa_records:
            return qa_records[0]

    @property
    def excessive_qa_records(self):
        qa_records = [qa_record for qa_record in self.self_records.all() if qa_record.excessive]
        return qa_records

    @property
    def can_work(self):
        if self.status == self.current_operation_record.status and self.qa_excessive_status == 1:
            return True
        else:
            return False

    @property
    def current_qa_records_excessive(self):
        if self.qa_excessive_status in [2,5,6]:
            return True
        else:
            return False

    @property
    def current_qa_records_passed(self):
        if self.qa_excessive_status in [7]:
            return True
        else:
            return False

    @property
    def current_qa_records_no_passed(self):
        if self.qa_excessive_status in [8]:
            return True
        else:
            return False

    @property
    def current_qa_records_decided(self):
        if self.qa_excessive_status in [7,8]:
            return True
        else:
            return False

    @property
    def current_qa_records_no_no_passed(self):
        if self.qa_excessive_status in [1,5]:
            return True
        else:
            return False

    @property
    def excessive(self):
        if self.qa_excessive_status in [1,3]:
            return False
        else:
            return True
    
    @property
    def excessived(self):
        if self.qa_excessive_status in [1]:
            return False
        else:
            return True
    
    @property
    def item_wait(self):
        if self.qa_excessive_status == 2:
            return True
        else:
            return False

    @property
    def item_pass(self):
        if self.qa_excessive_status == 3:
            return True
        else:
            return False

    @property
    def item_fail(self):
        if self.qa_excessive_status == 4:
            return True
        else:
            return False
    
    # #add barcode when saving
    # def save(self, *args, **kwargs):
    #     #add_barcode in yt_barcod.views
    #     #name = self.manu_item_group.product.name
    #     symbol = self.manu_item_group.product.symbol
    #     code = self.code
    #     #add_barcode(self, *args, **kwargs)
    #     add_barcode(symbol, code)
    #     super(self.__class__, self).save(*args, ** kwargs)


@receiver(post_save, sender=ManufactureItem)
def manufacture_item_post_save(sender, **kwargs):
    if kwargs['instance'].qa_excessive_status == 4:
        pass
    elif kwargs['instance'].qa_excessive_status == 3:
        pass
    elif kwargs['instance'].qa_excessive_status != 1:
        manufacture_items = kwargs['instance'].manu_item_group.manufacture_items.all()
        other_manufacture_items = []
        for manufacture_item in manufacture_items:
            if manufacture_item != kwargs['instance']:
                if not manufacture_item.current_qa_records_no_passed:
                    other_manufacture_items.append(manufacture_item)

        status_list = [manufacture_item.qa_excessive_status for manufacture_item in other_manufacture_items]
        if kwargs['instance'].qa_excessive_status == 2:
            if kwargs['instance'].manu_item_group.qa_excessive_status == 1:
                kwargs['instance'].manu_item_group.qa_excessive_status = 2
                kwargs['instance'].manu_item_group.save()
        elif kwargs['instance'].qa_excessive_status == 8:
            if 2 not in status_list and 5 not in status_list and 6 not in status_list:
                kwargs['instance'].manu_item_group.qa_excessive_status = 8
                kwargs['instance'].manu_item_group.save()
            else:
                kwargs['instance'].manu_item_group.qa_excessive_status = 6
                kwargs['instance'].manu_item_group.save()
        elif kwargs['instance'].qa_excessive_status == 7:
            if 2 not in status_list and 5 not in status_list and 6 not in status_list and 8 not in status_list:
                kwargs['instance'].manu_item_group.qa_excessive_status = 7
                kwargs['instance'].manu_item_group.save()
            elif 6 in status_list or 8 in status_list:
                kwargs['instance'].manu_item_group.qa_excessive_status = 6
                kwargs['instance'].manu_item_group.save()
            elif 6 not in status_list and 8 not in status_list:
                kwargs['instance'].manu_item_group.qa_excessive_status = 5
                kwargs['instance'].manu_item_group.save()
        elif kwargs['instance'].qa_excessive_status == 6:
            kwargs['instance'].manu_item_group.qa_excessive_status = 6
            kwargs['instance'].manu_item_group.save()
        elif kwargs['instance'].qa_excessive_status == 5:
            if 8 in status_list or 6 in status_list:
                kwargs['instance'].manu_item_group.qa_excessive_status = 6
                kwargs['instance'].manu_item_group.save()
            else:
                kwargs['instance'].manu_item_group.qa_excessive_status = 5
                kwargs['instance'].manu_item_group.save()




class ManufactureRecord(models.Model):
    '''
    生产记录
    '''
    date_added       = models.DateTimeField(auto_now_add=True, verbose_name=_("date_added"))
    operation_record = models.ForeignKey(OperationRecord, related_name="manufacture_records", verbose_name=_("operation_record"))
    manufacture_item = models.ForeignKey(ManufactureItem, related_name="manufacture_records", verbose_name=_("manufacture_item"))
    device_entry     = models.ForeignKey(DeviceEntry, related_name="manufacture_records", verbose_name=_("device_entry"))
    status           = models.PositiveSmallIntegerField(choices=CHOICE_STATE_STATUS, default=1, verbose_name=_("status"))


    def __unicode__(self):
        return "%s:%s" %(self.manufacture_item,self.operation_record)

    class Meta:

        verbose_name = _('ManufactureRecord')
        verbose_name_plural = _('ManufactureRecords')
        ordering = ('-manufacture_item',)


#create by xxd
CHOICE_RELATION_STATUS = (
    (1, _("wait")),
    (2, _("ok")),
    (3, _("reject")),
)
class ManufactureRelation(models.Model):
    from_manufacture_record = models.ForeignKey(ManufactureRecord, related_name="from_manufacture_relation", verbose_name=_("from_manufacture_record"))
    to_manufacture_record   = models.ForeignKey(ManufactureRecord, null=True, blank=True, related_name="to_manufacture_relation", verbose_name=_("from_manufacture_record"))
    from_employee    = models.ForeignKey(Employee, related_name="from_manufacture_relation", verbose_name=_("from_employee"))
    to_employee      = models.ForeignKey(Employee, null=True, blank=True, related_name="to_manufacture_relation", verbose_name=_("to_employee"))
    date             = models.DateField(verbose_name=_('date'))
    note             = models.CharField(max_length=255, verbose_name=_("note"))
    status           = models.PositiveSmallIntegerField(choices=CHOICE_RELATION_STATUS, default=1, verbose_name=_("status"))
    
    date_added      = models.DateTimeField(auto_now_add=True, verbose_name=_("date_added"))
    date_modified   = models.DateTimeField(auto_now=True, verbose_name=_("date_modified"))
    
    def __unicode__(self):
        return "%s" %(self.from_manufacture_record,)


CHOICE_RECORD_TYPE = (
    (1, _("QASelfRecord")),
    (2, _("QADoubleCheckRecord")),
    (3, _("QAInspectorRecord")),
)

class QARecord(models.Model):
    '''
    检验记录 -- QARecord

    包括自检，互检，检验记录
    **字段**
    employee            员工
    operation_record    工步记录
    manufacture_item    工件
    attributes          属性值（多个）
    type                自检/互检/检验
    created_at          创建日期
    updated_at          修改日期
    note                备注
    qa_excessive_status
    decider
    '''
    employee         = models.ForeignKey(Employee, related_name="self_records", verbose_name=_("qarecord employee"))
    operation_record = models.ForeignKey(OperationRecord, blank=True, null=True, related_name="self_records", verbose_name=_("operation_record"))
    manufacture_item = models.ForeignKey(ManufactureItem, blank=True, null=True, related_name="self_records", verbose_name=_("manufacture_item"))
    attributes       = models.ManyToManyField(Attribute, blank=True, null=True, through='QARecordAttribute', verbose_name=_("attributes"))
    type             = models.PositiveSmallIntegerField(choices=CHOICE_RECORD_TYPE, default=1, verbose_name=_("type"))
    created_at       = models.DateTimeField(auto_now_add=True, verbose_name=_("created_at"))
    updated_at       = models.DateTimeField(auto_now_add=True, auto_now=True, verbose_name=_("updated_at"))

    note             = models.CharField(blank=True, null=True, max_length=255, verbose_name=_("note"))
    qa_excessive_status = models.PositiveSmallIntegerField(choices=CHOICE_QA_EXCESSIVE_STATUS, default=1, verbose_name=_("qa_excessive_status"))
    
    decider          = models.ForeignKey(User, blank=True, null=True, verbose_name=_("qa decider"))

    # 新检验流程需要的字段
    # 检验时提交的备注
    check_note = models.CharField(blank=True, null=True, max_length=255, verbose_name=_("qa note"))
    # 检验人 （字符串或 qr code）
    surveyor_string = models.CharField(blank=True, null=True, max_length=255, verbose_name=_("surveyor"))

    def __unicode__(self):

        return "%s | %s | %s" %(self.manufacture_item,self.operation_record,self.get_type_display())

    class Meta:
        ordering = ('-updated_at',)
        verbose_name = _('QA Record')
        verbose_name_plural = _('QA Records')

#-------------------------------------------------------------------------------
    @property
    def is_type_qa_self_record(self):
        ''' 是否是自检记录 '''
        return self.type == 1
    @property
    def is_type_qa_double_check_record(self):
        ''' 是否互检记录 '''
        return self.type == 2
    @property
    def is_type_qa_inspector_record(self):
        ''' 是否检验记录 '''
        return self.type == 3

    @property
    def is_qa_excessive_status_normal(self):
        ''' 正常，默认的状态 '''
        return self.qa_excessive_status == 1
    @property
    def is_qa_excessive_status_excessive(self):
        ''' 出错，当产品出错且未处理时，置此状态 '''
        return self.qa_excessive_status == 2
    @property
    def is_qa_excessive_status_passed(self):
        ''' 原状态，表示通过，只有QARecordAttribute可以置此状态 '''
        return self.qa_excessive_status == 3
    @property
    def is_qa_excessive_status_no_passed(self):
        ''' 原状态，表示不通过，只有QARecordAttribute可以置此状态 '''
        return self.qa_excessive_status == 4
    @property
    def is_qa_excessive_status_passed_excessive(self):
        '''非原状态，至少有一个未处理状态，不得包含未通过状态'''
        return self.qa_excessive_status == 5
    @property
    def is_qa_excessive_status_no_passed_excessive(self):
        '''非原状态，至少有一个未处理状态，至少有一个未通过状态'''
        return self.qa_excessive_status == 6
    @property
    def is_qa_excessive_status_passed_decided(self):
        '''非原状态，不得包含未处理状态，不得包含未通过状态'''
        return self.qa_excessive_status == 7
    @property
    def is_qa_excessive_status_no_passed_decided(self):
        ''' 非原状态，不得包含未处理状态，至少有一个未通过状态 '''
        return self.qa_excessive_status == 8
    @property
    def is_excessive_qa_record_attributes_exists(self):
        '''
        函数说明：
            是否存在检验不合格的情况
        结果：
            1.如果存在(无论存在几个)，返回 True
            2.如果不存在，返回 False
        '''
        attributes = QARecordAttribute.objects.filter(qa_record=self)
        for att in attributes:
            if att.excessive:
                return True
        return False

    def set_qa_excessive_status_excessive(self, *args, **kwargs):
        self.qa_excessive_status = 2
        super(QARecord, self).save(*args, **kwargs)


    @property
    def self_reject_product_record(self):
        reject_product_records = self.reject_product_record.all()
        if reject_product_records:
            return reject_product_records[0]

    @property
    def decided(self):
        if self.qa_excessive_status in [1,7,8]:
            return True
        else:
            return False

    @property
    def passed(self):
        if self.qa_excessive_status == 5:
            return True
        else:
            return False

    @property
    def no_passed(self):
        if self.qa_excessive_status == 6:
            return True
        else:
            return False

    @property
    def excessive(self):
        if self.qa_excessive_status == 1:
            return False
        else:
            return True

    @property
    def item_wait(self):
        if self.qa_excessive_status == 2:
            return True
        else:
            return False

    @property
    def item_pass(self):
        if self.qa_excessive_status == 3:
            return True
        else:
            return False

    @property
    def item_fail(self):
        if self.qa_excessive_status == 4:
            return True
        else:
            return False

    @property
    def can_to_do(self):
        if self.qa_excessive_status in [3,4]:
            return False
        else:
            return True


@receiver(post_save, sender=QARecord ,dispatch_uid="unique_uid_qa_record_post_save")
def qa_record_post_save(sender, instance, **kwargs):
    use_new_check_flow = getattr(settings,'USE_NEW_CHECK_FLOW',False)
    if use_new_check_flow:
        pass
    else:
        # 原有的处理方式
        if instance.qa_excessive_status == 1:
            instance.manufacture_item.status = 3 + instance.type
            instance.manufacture_item.save()
            instance.operation_record.status = 3 + instance.type
            instance.operation_record.save()
        else:
            instance.manufacture_item.status = 2 + instance.type
            instance.manufacture_item.save()
            instance.operation_record.status = 2 + instance.type
            instance.operation_record.save()

        if instance.qa_excessive_status not in [1,instance.manufacture_item.qa_excessive_status]:
            instance.manufacture_item.qa_excessive_status = instance.qa_excessive_status
            instance.manufacture_item.save()
        if instance.operation_record.qa_excessive_status != instance.qa_excessive_status:
            instance.operation_record.qa_excessive_status = instance.qa_excessive_status
            instance.operation_record.save()

'''
qa_excessive_status
CHOICE_STATE_STATUS = (
    (1, _("Waiting")),
    (2, _("Working")),
    (3, _("QASelfRecord")),
    (4, _("QADoubleRecord")),
    (5, _("QAInspectorRecord")),
    (6, _("Finished")),
    (7, _("Error")),
    (8, _("Reworking")),
)
'''

# @receiver(post_save, sender=QARecord)
# def qa_record_post_save(sender, instance, **kwargs):
#     manufacture_item = instance.manufacture_item
#     operation_record = instance.operation_record
#     if instance.is_qa_excessive_status_normal:
#         manufacture_item.status = 3 + int(instance.type)
#         manufacture_item.save()

#         operation_record.status = 3 + int(instance.type)
#         operation_record.save()
#     elif instance.is_qa_excessive_status_passed:
#         logger.info('qa  passed')
#         # 检验通过了，继续下一个 检验 或 结束该工步
#         if instance.is_type_qa_self_record:
#             # 自检 => 互检
#             operation_record.status = 4
#             operation_record.save()

#             manufacture_item.status = 4
#             manufacture_item.save()
#         elif instance.is_type_qa_double_check_record:
#             # 互检 => 检验
#             operation_record.status = 5
#             operation_record.save()

#             manufacture_item.status = 5
#             manufacture_item.save()
#         elif instance.is_type_qa_inspector_record:
#             # 检验 => 结束
#             operation_record.status = 6
#             operation_record.save()

#             manufacture_item.status = 6
#             manufacture_item.save()
#     else:
#         manufacture_item.status = 2 + int(instance.type)
#         manufacture_item.save()
#         operation_record.status = 2 + int(instance.type)
#         operation_record.save()

#     if instance.qa_excessive_status not in [1,manufacture_item.qa_excessive_status]:
#         manufacture_item.qa_excessive_status = instance.qa_excessive_status
#         manufacture_item.save()

#     if operation_record.qa_excessive_status != instance.qa_excessive_status:
#         operation_record.qa_excessive_status = instance.qa_excessive_status
#         operation_record.save()





class QARecordAttribute(models.Model):

    qa_record      = models.ForeignKey(QARecord, related_name='qa_record_attributes', verbose_name=_('QArecord'))
    attribute      = models.ForeignKey(Attribute, related_name='with_record', verbose_name=_('attribute'))
    display_value  = models.CharField(max_length=255, verbose_name=_("display_value"))
    absolute_value = models.DecimalField(max_digits=22,decimal_places=3,blank=True,null=True, verbose_name=_('absolute_value'))
    is_published   = models.BooleanField(default=0, verbose_name=_('is_published'))
    
    note           = models.CharField(blank=True, null=True, max_length=255, verbose_name=_("note"))
    decide_people  = models.ForeignKey(User, blank=True, null=True, verbose_name=_("decide_people"))

    qa_excessive_status = models.PositiveSmallIntegerField(choices=CHOICE_QA_EXCESSIVE_STATUS, default=1, verbose_name=_("qa_excessive_status"))

    def __unicode__(self):

        return "%s(%s)" %(self.absolute_value, self.attribute.unit)

    class Meta:
        verbose_name = _('RecordAttribute')
        verbose_name_plural = _('RecordAttributes')
        ordering = ('-qa_record',)

    @property
    def product_attribute(self):
        product_attributes = OperationAttribute.objects.filter(
            operation=self.qa_record.operation_record.operation,
            attribute=self.attribute
        )
        if len(product_attributes) > 0:
            return product_attributes[0]

    @property
    def excessive(self):
        if self.qa_excessive_status in [2,3,4]:
            return True
        else:
            return False

    @property
    def passed(self):
        if self.qa_excessive_status == 3:
            return True
        else:
            return False

    @property
    def no_passed(self):
        if self.qa_excessive_status == 4:
            return True
        else:
            return False

# @receiver(pre_save, sender=QARecordAttribute)
# def qa_record_attribute_pre_save(sender, **kwargs):
#     # move to create_qa_record
#     if kwargs['instance'].qa_excessive_status == 1:
#         difference = kwargs['instance'].absolute_value - kwargs['instance'].product_attribute.absolute_value
#         if abs(kwargs['instance'].product_attribute.difference) < abs(difference):
#             kwargs['instance'].qa_excessive_status = 2
            
#             if kwargs['instance'].qa_record.qa_excessive_status != 2:
#                 kwargs['instance'].qa_record.qa_excessive_status = 2
#                 kwargs['instance'].qa_record.save()

#     #lase, to judge each record_attribute
#     if kwargs['instance'].qa_excessive_status != 1:
#         qa_record_attributes = kwargs['instance'].qa_record.qa_record_attributes.all()
#         status_list = [qa_record_attribute.qa_excessive_status for qa_record_attribute in qa_record_attributes if qa_record_attribute != kwargs['instance']]
#         if kwargs['instance'].qa_excessive_status == 3:
#             if 2 in status_list and 4 in status_list:
#                 kwargs['instance'].qa_record.qa_excessive_status = 6
#                 kwargs['instance'].qa_record.save()
#             elif 2 in status_list:
#                 kwargs['instance'].qa_record.qa_excessive_status = 5
#                 kwargs['instance'].qa_record.save()
#             elif 2 not in status_list and 4 in status_list:
#                 kwargs['instance'].qa_record.qa_excessive_status = 8
#                 kwargs['instance'].qa_record.save()
#             elif 2 not in status_list and 3 in status_list:
#                 kwargs['instance'].qa_record.qa_excessive_status = 7
#                 kwargs['instance'].qa_record.save()
#             elif 1 in status_list:
#                 kwargs['instance'].qa_record.qa_excessive_status = 7
#                 kwargs['instance'].qa_record.save()
#         elif kwargs['instance'].qa_excessive_status == 4:
#             if 2 in status_list:
#                 kwargs['instance'].qa_record.qa_excessive_status = 6
#                 kwargs['instance'].qa_record.save()
#             elif 2 not in status_list:
#                 kwargs['instance'].qa_record.qa_excessive_status = 8
#                 kwargs['instance'].qa_record.save()


CHOICE_TODO_TYPE = (
    (1, _("Waiting")),        #等待处理
    (2, _("Rework")),         #返修
    (3, _("Degrade")),        #降级
    (4, _("Scrap")),          #报废
)

class RejectProductRecord(YTObject):
    productionline     = models.ForeignKey(ProductionLine, related_name="reject_product_records", verbose_name=_("productionline"))
    qa_record          = models.ForeignKey(QARecord, unique=True, related_name='reject_product_record', verbose_name=_('qa_record'))
    quality_problems   = models.CharField(max_length=255, verbose_name=_("quality_problems"))
    reason_analysis    = models.CharField(max_length=255, verbose_name=_("reason_analysis"))
    processing_result  = models.CharField(max_length=255, verbose_name=_("processing_result"))
    todo_type          = models.PositiveSmallIntegerField(choices=CHOICE_TODO_TYPE, default=1, verbose_name=_("todo_type"))
    
    decider            = models.ForeignKey(User, blank=True, null=True, verbose_name=_("reject decider"))
    
    def __unicode__(self):

        return "%s" %(self.qa_record.manufacture_item,)

    class Meta:
        verbose_name = _('RejectProductRecord')
        verbose_name_plural = _('RejectProductRecords')
        ordering = ('-productionline',)
