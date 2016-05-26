#-*- coding: UTF-8 -*- 
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.http import HttpResponseRedirect
from django.db.models.signals import pre_save, pre_delete
from django.dispatch import receiver
from django.contrib.contenttypes.models import ContentType
#from thirdparty
from workflows.models import *
from workflows.utils import *
from productcatalog.models import Product, Attribute
#from lili, edit by xxd
from person.models import Employee, Job
#from xxd
from yt_file.models import File, FileDirectory
from companydepartment.models import Company
from yt_log.models import StateDetail, WorkflowLog
#from lxy
from device.models import *
from material.models import *

CHOICE_STATUS_STATE = (
    (1, _("Normal")),
    (2, _("Invalid")),
    (3, _("Old Rev")),
)
##########################
#util
##########################
def find_technology_workflow_executor(technology,name):
    workflow                  = get_workflow(technology)
    technology_type           = ContentType.objects.get_for_model(technology)
    workflow_object_relation  = WorkflowObjectRelation.objects.get(content_type__pk=technology_type.id,content_id=technology.id)
    state                     = State.objects.get(workflow=workflow,name=name)
    state_detail              = StateDetail.objects.get(workflow_object_relation=workflow_object_relation,state=state)
    workflow_logs             = WorkflowLog.objects.filter(state_detail=state_detail,type=1).order_by('-id')
    if workflow_logs:
        return workflow_logs[0]
    else:
        return _('waiting...')

class Technology(models.Model):
#-------------------------------------------------------------------------------
    """
    工艺

    **字段**
    code                            编号
    product                         图号
    name                            工艺名称
    description                     工艺描述
    workflow                        工艺流程
    publish_code                    发放号
    file_code                       工艺文件编号
    materials                       材料
    each_product                    每个产品
    spare_part                      备件
    total                           总计
    one_piece                       单件
    complete_set                    全套
    workblank_mark                  毛坯牌号
    workblank_standard_code         毛坯标准代号
    workblank_hardness              毛坯硬度
    workblank_species               毛坯种类
    workblank_sectional_dimensions  毛坯剖面尺寸
    workblank_length                毛坯长度
    workblank_quantity              毛坯数量
    workblank_single_weight_kg      毛坯单件质量kg
    workblank_full_weight_kg        毛坯全套质量kg
    status                          状态
    """
#-------------------------------------------------------------------------------
    code          = models.CharField(max_length=100, verbose_name=_("code"))
    product       = models.ForeignKey(Product, related_name="technology", verbose_name=_("technology code"))
    name          = models.CharField(max_length=100, blank=True, null=True, verbose_name=_("technology name"))
    description   = models.CharField(max_length=250, blank=True, null=True, verbose_name=_("technology description"))
    workflow      = models.ForeignKey(Workflow, blank=True, null=True, related_name="technology", verbose_name=_("workflow"))
    #company       = models.ForeignKey(Company, blank=True, null=True, related_name="technologies", verbose_name=_("company"))
    publish_code  = models.CharField(max_length=100, blank=True, null=True, verbose_name=_("publish_code"))
    
    file_code     = models.CharField(max_length=100, blank=True, null=True, verbose_name=_("technology file code"))
    materials     = models.ManyToManyField(Material, blank=True, null=True, related_name="materials_technology", verbose_name=_("materials"))
    
    each_product = models.CharField(max_length=100, blank=True, null=True, verbose_name=_("each product"))
    spare_part = models.CharField(max_length=100, blank=True, null=True, verbose_name=_("spare part"))
    total = models.CharField(max_length=100, blank=True, null=True, verbose_name=_("total"))
    one_piece = models.CharField(max_length=100, blank=True, null=True, verbose_name=_("one piece"))
    complete_set = models.CharField(max_length=100, blank=True, null=True, verbose_name=_("complete set"))
    
    workblank_mark             = models.CharField(max_length=100, blank=True, null=True, verbose_name=_("workblank_mark"))
    workblank_standard_code    = models.CharField(max_length=100, blank=True, null=True, verbose_name=_("workblank_standard_code"))
    workblank_hardness         = models.CharField(max_length=100, blank=True, null=True, verbose_name=_("workblank_hardness"))
    workblank_species          = models.CharField(max_length=100, blank=True, null=True, verbose_name=_("workblank_species"))
    workblank_sectional_dimensions = models.CharField(max_length=100, blank=True, null=True, verbose_name=_("workblank_sectional_dimensions"))
    workblank_length           = models.CharField(max_length=100, blank=True, null=True, verbose_name=_("workblank_length"))
    workblank_quantity         = models.CharField(max_length=100, blank=True, null=True, verbose_name=_("workblank_quantity"))
    workblank_single_weight_kg = models.CharField(max_length=100, blank=True, null=True, verbose_name=_("workblank_single_weight_kg"))
    workblank_full_weight_kg   = models.CharField(max_length=100, blank=True, null=True, verbose_name=_("workblank_full_weight_kg"))
    
    status        = models.PositiveSmallIntegerField(choices=CHOICE_STATUS_STATE, default=1, verbose_name=_("status"))

    # created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    # updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('technology')
        verbose_name_plural = _('technologies')
        ordering = ("-id", )
        permissions = (
            ("start_technology_workflow", "Can Start Technology Workflow"),
            ("show_technology_workflow", "Can Show Technology Workflow"),
        )

    def __unicode__(self):
        return "%s:%s" %(self.name, self.code)
#-------------------------------------------------------------------------------
    def save(self, *args, **kwargs):
        super(self.__class__, self).save(*args, ** kwargs)
    
    @property
    def operations(self):
        ''' 返回当前工艺下的所有工步 '''
        operation_groups = self.operation_groups.all()
        operations = Operation.objects.none()
        for og in operation_groups:
            operations = operations | og.operations.all()
        return operations

    @property
    def operations_attribute_needs(self):
        ''' 返回所有需要创建属性的工步 '''
        operation_list = []
        operations = self.operations
        for operation in operations:
            if operation.is_attribute_exists and not operation.attributes.all():
                operation_list.append(operation)
        return operation_list

    @property
    def rev_order(self):
        rev_num = self.rev.all()[0].order if self.rev.all() else 1
        return "%02d" % rev_num

    @property
    def is_latest_rev(self):
        if self.children_rev.all():
            return False
        else:
            return True

    @property
    def files(self):
        fileowner_type = ContentType.objects.get_for_model(self)
        files = File.objects.filter(content_type__pk=fileowner_type.id,object_id=self.id).order_by('-date_added')
        return files
    
    @property
    def directory_files(self):
        fileowner_type = ContentType.objects.get_for_model(self)
        directory_files = FileDirectory.objects.filter(is_active=True,content_type__pk=fileowner_type.id,object_id=self.id).order_by('-date_added')
        return directory_files
    
    @property
    def file(self):
        fileowner_type = ContentType.objects.get_for_model(self)
        files = File.objects.filter(content_type__pk=fileowner_type.id,object_id=self.id).order_by('-date_added')
        if files:
            return files[0]
        else:
            return None
    
    @property
    def T_file(self):
        ''' 工艺文件 '''
        fileowner_type = ContentType.objects.get_for_model(self)
        files = FileDirectory.objects.filter(
            content_type__pk=fileowner_type.id,
            object_id=self.id,
            is_active=True,
            name__startswith="T_"
        ).order_by('-date_added')
        if files:
            return files[0]
        else:
            return None
    @property
    def P_file(self):
        ''' 程式文件 '''
        fileowner_type = ContentType.objects.get_for_model(self)
        files = FileDirectory.objects.filter(
            content_type__pk=fileowner_type.id,
            object_id=self.id,
            is_active=True,
            name__startswith="P_"
        ).order_by('-date_added')
        if files:
            return files[0]
        else:
            return None
    @property
    def D2_file(self):
        fileowner_type = ContentType.objects.get_for_model(self)
        files = FileDirectory.objects.filter(
            content_type__pk=fileowner_type.id,
            object_id=self.id,
            is_active=True,
            name__startswith="D2_"
        ).order_by('-date_added')
        if files:
            return files[0]
        else:
            return None
    @property
    def D3_file(self):
        fileowner_type = ContentType.objects.get_for_model(self)
        files = FileDirectory.objects.filter(
            content_type__pk=fileowner_type.id,
            object_id=self.id,
            is_active=True,
            name__startswith="D3_"
        ).order_by('-date_added')
        if files:
            return files[0]
        else:
            return None

    @property
    def product_symbol(self):
        return self.product.symbol

    @property
    def bianzhi(self):
        return find_technology_workflow_executor(self,'编制')

    @property
    def shenhe(self):
        return find_technology_workflow_executor(self,'审核')

    @property
    def biaozhunhua(self):
        return find_technology_workflow_executor(self,'标准化')

    @property
    def huiqian(self):
        return find_technology_workflow_executor(self,'会签')

    @property
    def pizhun(self):
        return find_technology_workflow_executor(self,'批准')

    @property
    def init_workflow_status(self):
        if self.technology_workflow_status == 2:
            if self.workflow:
                return 2#init finished
            else:
                return 0#wait for init
        else:
            return 1#cannot init

    @property
    def technology_workflow_status(self):
        if self.T_file:
            workflow = get_workflow(self)
            if workflow:
                current_state = get_state(self)
                if current_state.transitions.all():
                    return 1#started
                else:
                    return 2#finished
            else:
                return 0#wait for start
        else:
            return 3#no technology file

    @property
    def is_technology_workflow_status_wait_for_start(self):
        return self.technology_workflow_status == 0
    @property
    def is_technology_workflow_status_started(self):
        return self.technology_workflow_status == 1
    @property
    def is_technology_workflow_status_finished(self):
        return self.technology_workflow_status == 2
    @property
    def is_technology_workflow_status_no_technology_file(self):
        return self.technology_workflow_status == 3


    @property
    def technology_workflow_approved(self):
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
        technology_type          = ContentType.objects.get_for_model(self)
        workflow_object_relation = WorkflowObjectRelation.objects.get(content_type__pk=technology_type.id,content_id=self.id)
        current_state            = get_state(self)
        state_detail             = StateDetail.objects.get(workflow_object_relation=workflow_object_relation,state=current_state)
        return state_detail
    
    @property
    def workflow_object_relation(self):
        technology_type          = ContentType.objects.get_for_model(self)
        workflow_object_relation = WorkflowObjectRelation.objects.get(content_type__pk=technology_type.id,content_id=self.id)
        return workflow_object_relation

@receiver(pre_delete, sender=Technology)
def technology_pre_delete(sender, **kwargs):
    self = kwargs['instance']
    self.directory_files.delete()
    self.files.delete()

class OperationGroup(models.Model):
    '''
    工序

    **字段**
    name            工序名称
    description     工序描述
    technology      工艺
    order           工序号
    Job             岗位
    device          设备
    materials       材料
    coolant         冷却剂
    material_mark   材料牌号
    fixture         夹具
    '''
    name          = models.CharField(max_length=100, blank=True, null=True, verbose_name=_("operation group name"))
    description   = models.CharField(max_length=250, blank=True, null=True, verbose_name=_("operation group description"))
    technology    = models.ForeignKey(Technology, related_name="operation_groups", verbose_name=_("technology"))
    order         = models.IntegerField(verbose_name=_("operation group order"))
    Job           = models.ForeignKey(Job, blank=True, null=True, related_name="operation_groups", verbose_name=_("job"))
    
    device        = models.ForeignKey(Device, blank=True, null=True, related_name="operation_groups", verbose_name=_("device"))
    materials     = models.ManyToManyField(Material, blank=True, null=True, related_name="operation_groups", verbose_name=_("materials"))
    #tools = models.ManyToManyField(Tool, blank=True, null=True, related_name="operation_groups", verbose_name=_("tools"))

    coolant       = models.CharField(max_length=200, blank=True, null=True, verbose_name=_("coolant"))
    material_mark = models.CharField(max_length=100, blank=True, null=True, verbose_name=_("material_mark"))
    fixture       = models.CharField(max_length=200, blank=True, null=True, verbose_name=_("fixture"))
    
    class Meta:
        verbose_name = _('operation_group')
        verbose_name_plural = _('operation_groups')
        # unique_together = ('technology', 'order',)
        ordering = ("technology", "order", )

    def __unicode__(self):
        return "%s" %(self.name)
#-------------------------------------------------------------------------------
    @property
    def device_item(self):
        from warehouse.models import Item
        device_type = ContentType.objects.get_for_model(self.device)
        device_item = Item.objects.get(
            content_type_id = device_type.id,
            object_id = self.device.id,
        )
        return device_item

    @property
    def TU1_file(self):
        fileowner_type = ContentType.objects.get_for_model(self)
        files = FileDirectory.objects.filter(
            content_type__pk=fileowner_type.id,
            object_id=self.id,
            is_active=True,
            name__startswith="TU1_"
        ).order_by('-date_added')
        if files:
            return files[0]
        else:
            return None
            
    @property
    def TU2_file(self):
        fileowner_type = ContentType.objects.get_for_model(self)
        files = FileDirectory.objects.filter(
            content_type__pk=fileowner_type.id,
            object_id=self.id,
            is_active=True,
            name__startswith="TU2_"
        ).order_by('-date_added')
        if files:
            return files[0]
        else:
            return None
            
    @property
    def TU3_file(self):
        fileowner_type = ContentType.objects.get_for_model(self)
        files = FileDirectory.objects.filter(
            content_type__pk=fileowner_type.id,
            object_id=self.id,
            is_active=True,
            name__startswith="TU3_"
        ).order_by('-date_added')
        if files:
            return files[0]
        else:
            return None

    @property
    def files(self):
        fileowner_type = ContentType.objects.get_for_model(self)
        files = File.objects.filter(content_type__pk=fileowner_type.id,object_id=self.id).order_by('-date_added')
        return files
    
    @property
    def directory_files(self):
        fileowner_type = ContentType.objects.get_for_model(self)
        directory_files = FileDirectory.objects.filter(is_active=True,content_type__pk=fileowner_type.id,object_id=self.id).order_by('-date_added')
        return directory_files
    
    @property
    def images(self):
        import base64
        from yt_file.models import File, FileDirectory
        from extensions.custom_fields.encrypt import decode_notin_field

        files_data = []
        fileowner_type = ContentType.objects.get_for_model(self)
        files = FileDirectory.objects.filter(is_active=True,content_type__pk=fileowner_type.id,object_id=self.id,status=1,imgtag=1).order_by('id')
        # for file in files:
        #     #content = decode_notin_field(file.data)#to see custom_fields.encrypt
        #     if file.imgtag:
        #         file_data = "data:image/jpeg;base64,"+base64.b64encode(file.data)
        #         files_data.append([file_data,file.id])
        return files
        
    @property
    def D2_file(self):
        fileowner_type = ContentType.objects.get_for_model(self)
        files = FileDirectory.objects.filter(
            content_type__pk=fileowner_type.id,
            object_id=self.id,
            is_active=True,
            name__startswith="D2_"
        ).order_by('-date_added')
        if files:
            return files[0]
        else:
            return None
    @property
    def D3_file(self):
        fileowner_type = ContentType.objects.get_for_model(self)
        files = FileDirectory.objects.filter(
            content_type__pk=fileowner_type.id,
            object_id=self.id,
            is_active=True,
            name__startswith="D3_"
        ).order_by('-date_added')
        if files:
            return files[0]
        else:
            return None

@receiver(pre_delete, sender=OperationGroup)
def operation_group_pre_delete(sender, **kwargs):
    self = kwargs['instance']
    self.directory_files.delete()
    self.files.delete()


CHOICE_OPERATION_TYPE = (
    (1, _("General")),
    (2, _("Cooling")),
)

class OperationType(models.Model):
    name = models.CharField(max_length=250, unique=True, verbose_name=_("name"))

    def __unicode__(self):
        return "%s" %(self.name)

CHOICE_NEED_ATTRIBUTES = (
    (1,_("Not Required")),
    (2,_("Maybe")),
    (3,_("Required")),
)

class Operation(models.Model):
    '''
    工步

    **字段**
    name                    工步名称
    description             工步描述
    operation_group         工序
    order                   工步号
    state                   状态
    product                 半成品
    knifes                  刀具
    tools                   工量具
    period                  时效(小时)
    operation_type          类型
    attributes              属性
    equipment               工艺装备
    '''
    name             = models.CharField(max_length=250, blank=True, null=True, verbose_name=_("operation name"))
    description      = models.CharField(max_length=250, blank=True, null=True, verbose_name=_("operation description"))
    operation_group  = models.ForeignKey(OperationGroup, related_name="operations", verbose_name=_("operation_groups"))
    order            = models.IntegerField(verbose_name=_("operation order"))
    state            = models.ForeignKey(State, blank=True, null=True, related_name="operation", verbose_name=_("state"))
    
    product          = models.ForeignKey(Product, blank=True, null=True, related_name="operations", verbose_name=_("semifinished_product"))
    knifes           = models.ManyToManyField(Knife, blank=True, null=True, related_name="operations", verbose_name=_("knifes"))
    tools            = models.ManyToManyField(Tool, blank=True, null=True, related_name="operations", verbose_name=_("tool measure"))
    period           = models.IntegerField(blank=True, null=True, verbose_name=_("period(hours)"))
    operation_type   = models.ForeignKey(OperationType, default=1, related_name="operations", verbose_name=_("type"))
    
    attributes       = models.ManyToManyField(Attribute, through='OperationAttribute', verbose_name=_('attributes'))
    equipment        = models.CharField(max_length=50, blank=True, null=True, verbose_name=_("equipment"))
    
    # 是否需要处理工步属性 不需要 / 可能需要 / 需要
    need_attribute = models.PositiveSmallIntegerField(
                choices=CHOICE_NEED_ATTRIBUTES,
                default=1,
                verbose_name=_("need attribute"),
        )

    class Meta:
        verbose_name = _('operation')
        verbose_name_plural = _('operations')
        #TODO:operation_group->technology
        unique_together = ('operation_group', 'order',)
        ordering = ("operation_group","order", )

    def __unicode__(self):
        return "%s" %(self.name)

    @property
    def is_attribute_exists(self):
        '''
        是否存在检验属性
            1. 存在 ： 需要添加工步属性之后才能开始审核
            2. 可能存在： 工作人员需要添加属性或者修改为不需要
            3. 不存在 ：  不需要操作
        返回：
            1. 需要检验和可能需要建议都返回 True
            2. 不需要检验返回 False
        '''
        if self.need_attribute == 2 or self.need_attribute == 3:
            return True
        return False
    @property
    def is_need_attribute_required(self):
        """
        检验属性是必须添加的
        """
        return self.need_attribute == 3
    @property
    def is_need_attribute_maybe_required(self):
        """
        检验属性可能需要添加，有工作人员确定
        """
        return self.need_attribute == 2
    @property
    def is_need_attribute_not_requried(self):
        """
        不需要添加检验属性
        """
        return self.need_attribute == 1

    def set_need_attribute_not_required(self, *args, **kwargs):
        self.need_attribute = 1
        super(Operation, self).save(*args, **kwargs)
    def set_need_attribute_maybe_required(self, *args, **kwargs):
        self.need_attribute = 2
        super(Operation, self).save(*args, **kwargs)
    def set_need_attribute_required(self, *args, **kwargs):
        self.need_attribute = 3
        super(Operation, self).save(*args, **kwargs)

class OperationAttribute(models.Model):
    operation       = models.ForeignKey(Operation, related_name="operation_attributes", verbose_name=_('operation'))
    attribute       = models.ForeignKey(Attribute, verbose_name=_('attribute name'), related_name='operation_attributes')
    display_value   = models.CharField(_('display value'),default="",max_length=255,blank=True,null=True)
    absolute_value  = models.DecimalField(_('absolute value'),max_digits=22,decimal_places=3)
    is_published    = models.BooleanField(_('is published'),default=True)
    ext_code        = models.CharField(max_length=128, null=True, blank=True)
    difference      = models.DecimalField(_('difference'),default=0,max_digits=22,decimal_places=3)

    upper_deviation = models.DecimalField(_('upper_deviation'),default=0,max_digits=22,decimal_places=3)
    lower_deviation = models.DecimalField(_('lower_deviation'),default=0,max_digits=22,decimal_places=3)


    class Meta:
        verbose_name = _('OperationAttribute')
        verbose_name_plural = _('OperationAttributes')
        ordering = ('-operation',)

    def __unicode__(self):

        return "%s(%s)" %(self.absolute_value, self.attribute.unit)

class TechnologyRev(models.Model):
    created_at  = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at  = models.DateTimeField(_('updated at'), auto_now=True)
    order       = models.IntegerField(verbose_name=_("rev order"))
    parent      = models.ForeignKey(Technology, related_name="children_rev", verbose_name=_("parent technology"))
    child       = models.ForeignKey(Technology, unique=True, related_name="rev", verbose_name=_("child technology"))
    code        = models.CharField(max_length=100, blank=True, null=True, verbose_name=_("rev code"))
    note        = models.CharField(max_length=100, blank=True, null=True, verbose_name=_("rev note"))
    updated_by  = models.ForeignKey(User, verbose_name=_("updated by"))

    class Meta:
        verbose_name = _('TechnologyRev')
        verbose_name_plural = _('TechnologyRevs')
        ordering = ("parent", "-order")

    def __unicode__(self):
        return "%s:%s" %(self.child, self.code)
