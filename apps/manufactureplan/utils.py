#-*- coding: UTF-8 -*- 

from django.conf import settings
from django.db.models import Q
from workflows.utils import do_transition , get_state, get_allowed_transitions

from .models import ManufactureItem
from .models import ManufactureItemGroup

from django.utils.log import logger

#-------------------------------------------------------------------------------
# 返回 ManufactureItem
def get_all_check_manu_items(is_use_attributes=False,is_user_operation_group_name=True):
    '''
    函数说明：
        返回状态为 检验的 所有工件
    参数说明：
        1. is_use_attributes 根据 atributes 来获取 工件，
        2. is_user_operation_group_name 根据工件当前工序名称来获取工件
    返回值：
        满足条件的 ManufactureItem 的id 列表
    '''
    if is_use_attributes:
        queryset = ManufactureItem.objects.filter(productionline__current_operation_record__operation__attributes__isnull=False)
    elif is_user_operation_group_name:
        queryset = ManufactureItem.objects.filter(Q(productionline__current_operation_record__oper_group_record__operation_group__name=u'毛坯检验')|Q(productionline__current_operation_record__oper_group_record__operation_group__name=u'终检'))
    else:
        queryset = ManufactureItem.objects.filter(productionline__current_operation_record__operation__attributes__isnull=False).filter(status=5)
    use_new_check_flow = getattr(settings,'USE_NEW_CHECK_FLOW',False)
    if use_new_check_flow:
        # 合格/不合格/未处理 ，这里只返回未处理的工件
        mis_id_list = queryset.filter(productionline__current_operation_record__quality_status=0).values_list('id',flat=True)
    else:
        mis_id_list = queryset.filter().values_list('id',flat=True)
    return mis_id_list

def get_all_wipe_burr_manu_items(is_use_attributes=True):
    '''
    函数说明：
        返回当前工序为 去毛刺 的工件
    参数说明：
        1. is_use_attributes 是否包含 带有 检验属性的 工件，False 表示不包含
    '''
    queryset = ManufactureItem.objects.filter(productionline__current_operation_record__oper_group_record__operation_group__name=u'去毛刺')
    if not is_use_attributes:
        queryset.filter(productionline__current_operation_record__operation__attributes__isnull=False)
    mis_id_list = queryset.filter().values_list('id',flat=True)
    return mis_id_list

def get_all_heattreatment_manu_items(is_use_attributes=True):
    '''
    函数说明：
        返回当前工序为 热处理 的工件
    参数说明：
        1. is_use_attributes 是否包含 带有 检验属性的 工件，False 表示不包含
    '''
    queryset = ManufactureItem.objects.filter(productionline__current_operation_record__oper_group_record__operation_group__name=u'热处理')
    if not is_use_attributes:
        queryset.filter(productionline__current_operation_record__operation__attributes__isnull=False)
    mis_id_list = queryset.filter().values_list('id',flat=True)
    return mis_id_list

def get_all_incasement_manu_items(is_use_attributes=True):
    '''
    函数说明：
        返回当前工序为 装箱 的工件
    参数说明：
        1. is_use_attributes 是否包含 带有 检验属性的 工件，False 表示不包含
    '''
    queryset = ManufactureItem.objects.filter(productionline__current_operation_record__oper_group_record__operation_group__name=u'装箱')
    if not is_use_attributes:
        queryset.filter(productionline__current_operation_record__operation__attributes__isnull=False)
    mis_id_list = queryset.filter().values_list('id',flat=True)
    return mis_id_list

def get_all_period_manu_items(is_use_attributes=True):
    '''
    函数说明：
        返回当前工序为 时效 的工件
    参数说明：
        1. is_use_attributes 是否包含 带有 检验属性的 工件，False 表示不包含
    '''
    queryset = ManufactureItem.objects.filter(productionline__current_operation_record__oper_group_record__operation_group__name=u'时效')
    if not is_use_attributes:
        queryset.filter(productionline__current_operation_record__operation__attributes__isnull=False)
    mis_id_list = queryset.filter().values_list('id',flat=True)
    return mis_id_list

#-------------------------------------------------------------------------------
def get_batch_productionlines(batch_type):
    '''
    函数说明：
        返回可以批量 处理的 productionlines
    参数说明：
        1. batch_type 批量处理类型：  检验/去毛刺/热处理/装箱/时效
    '''
    # 1. 获取工件
    if batch_type == 'check':
        mis_id_list = get_all_check_manu_items()
    elif batch_type == 'wipe_burr':
        mis_id_list = get_all_wipe_burr_manu_items()
    elif batch_type == 'heattreatment':
        mis_id_list = get_all_heattreatment_manu_items()
    elif batch_type == 'incasement':
        mis_id_list = get_all_incasement_manu_items()
    elif batch_type == 'period':
        mis_id_list = get_all_period_manu_items()
    else:
        mis_id_list = set()

    # 2. 获取 工件组
    migs_id_list = set(ManufactureItem.objects.filter(id__in=mis_id_list).values_list('manu_item_group',flat=True))

    # 3. 找到 productionline
    productionline_id_list = set(ManufactureItemGroup.objects.filter(id__in=migs_id_list).values_list('productionline',flat=True))

    # 返回结果
    return productionline_id_list


def get_all_batch_handle_productionlines():
    '''
    函数说明：
        返回所有可以批量处理的 productionlines

    '''
    # 是否启用批量检验
    is_contains_batch_check = getattr(settings,'IS_USE_BATCH_CHECK',False)

    mis_id_list_wipe_burr = get_all_wipe_burr_manu_items()
    mis_id_list_heattreatment = get_all_heattreatment_manu_items()
    mis_id_list_incasement = get_all_incasement_manu_items()
    mis_id_list_period = get_all_period_manu_items()

    mis = ManufactureItem.objects.filter(Q(id__in=mis_id_list_wipe_burr)|Q(
        id__in=mis_id_list_heattreatment)|Q(
        id__in=mis_id_list_incasement)|Q(
        id__in=mis_id_list_period))

    migs_id_list = set(mis.values_list('manu_item_group',flat=True))

    productionline_id_list = set(ManufactureItemGroup.objects.filter(id__in=migs_id_list).values_list('productionline',flat=True))

    if is_contains_batch_check:
        batch_check_productionlines = get_batch_productionlines(batch_type='check')
        # 和 批量检验 取并集
        productionline_id_list = set(productionline_id_list).union(set(batch_check_productionlines))
    return productionline_id_list


def get_mis_id_list_other():
    '''
    函数说明：
        工作台 `其它` 中显示的工件
    '''

    is_contains_batch_check = getattr(settings,'IS_USE_BATCH_CHECK',False)
    use_new_check_flow = getattr(settings,'USE_NEW_CHECK_FLOW',False)


    mis_id_list = get_all_check_manu_items()

    multi_mis_id_list = set(ManufactureItem.objects.filter(Q(
        productionline__current_operation_record__oper_group_record__operation_group__name=u'去毛刺')|Q(
        productionline__current_operation_record__oper_group_record__operation_group__name=u'热处理')|Q(
        productionline__current_operation_record__oper_group_record__operation_group__name=u'装箱')|Q(
        productionline__current_operation_record__oper_group_record__operation_group__name=u'时效')).values_list('id',flat=True))

    queryset = ManufactureItem.objects.exclude(id__in=multi_mis_id_list)
    if is_contains_batch_check:
        # 如果批量检验功能完成，这里就可以排除了
        queryset = queryset.exclude(id__in=mis_id_list)

    # 排除不合格的工件
    if use_new_check_flow:
        queryset = queryset.exclude(productionline__current_operation_record__quality_status=2)

    result_mis_id_list = queryset.values_list('id',flat=True)

    return result_mis_id_list


def productionline_do_transition(user,productionline,status):
    # import pdb; pdb.set_trace()
    result = 0

    #set current_operation_record status
    current_operation_record = productionline.current_operation_record
    current_operation_record.status = status
    current_operation_record.save()
    # logger.info(current_operation_record.status)

    transitions = get_allowed_transitions(productionline,user)
    # logger.info(transitions)
    if len(transitions) > 0:
        do_transition(productionline,transitions[0],user)

        #get current_operation_record
        current_state = get_state(productionline)
        for oper_group_record in productionline.oper_group_records.all():
            for operation_record in oper_group_record.operation_records.all():
                if operation_record.operation.state == current_state:
                    current_operation_record = operation_record

        #set productionline current_operation_record
        productionline.current_operation_record = current_operation_record
        productionline.save()

        #set current_operation_record status
        productionline.current_operation_record.status = 2
        productionline.current_operation_record.save()

        #set parent_operation_record status
        parent_operation_record = current_operation_record.parent_operation_record
        if parent_operation_record.status == 1:
            parent_operation_record.status = 2
            parent_operation_record.save()

        #set manufacture_item.status
        for manufacture_item in productionline.manufacture_items.all():
            manufacture_item.status = 2
            manufacture_item.save()


        #parent_productionline do_transition
        parent_productionline = productionline.parent_productionline
        order_code = parent_productionline.current_operation_record.order_code
        can_do_parent_transition_tag = True
        for mig in parent_productionline.manu_item_groups.all():
            for mi in mig.manufacture_items.all():
                if mi.current_operation_record.order_code <= order_code:
                    can_do_parent_transition_tag = False
        if can_do_parent_transition_tag:
            #set parent_current_operation_record status
            parent_current_operation_record = parent_productionline.current_operation_record
            parent_current_operation_record.status = status
            parent_current_operation_record.save()
            #do_transition
            parent_transitions = get_allowed_transitions(parent_productionline,user)
            if len(parent_transitions) > 0:
                do_transition(parent_productionline,parent_transitions[0],user)
                #get parent_current_operation_record
                current_state = get_state(parent_productionline)
                for oper_group_record in parent_productionline.oper_group_records.all():
                    for operation_record in oper_group_record.operation_records.all():
                        if operation_record.operation.state == current_state:
                            parent_current_operation_record = operation_record
                #set parent_current_operation_record status
                parent_productionline.current_operation_record = parent_current_operation_record
                parent_productionline.save()
                #set parent_current_operation_record status
                parent_productionline.current_operation_record.status = 2
                parent_productionline.current_operation_record.save()
            else:
                #do parent_productionline finish
                parent_productionline.state = 3
                parent_productionline.save()
                return 0
    else:
        #do parent_productionline finish
        productionline.state = 3
        productionline.save()
        
        parent_productionline = productionline.parent_productionline
        can_do_parent_transition_tag = True
        for mig in parent_productionline.manu_item_groups.all():
            for mi in mig.manufacture_items.all():
                if mi.productionline.state != 3:
                    can_do_parent_transition_tag = False
        if can_do_parent_transition_tag:
            #set parent_current_operation_record status
            parent_current_operation_record = parent_productionline.current_operation_record
            parent_current_operation_record.status = status
            parent_current_operation_record.save()
            #do parent_productionline finish
            parent_productionline.state = 3
            parent_productionline.save()
            return 0
        return 0
    return result