#-*- coding: UTF-8 -*- 
from django.shortcuts import render_to_response,render
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.decorators import login_required
from django.utils.translation import ugettext_lazy as _
import json
import re

#from thirdparty
from workflows.models import *
from workflows.utils import *
from permissions.models import *
from permissions.utils import *
#from xxd
from models import Technology, OperationGroup, Operation, OperationType
from forms import *
from yt_log.models import WorkflowLog, StateDetail
from yt_file.models import File, FileDirectory
from notification.models import *
from notification.yt_views import *
from person.models import *
from device.models import *
from settings import UPLOAD_ROOT, UPLOAD_URL, TECHNOLOGY_TEMPLATE_LATEST_URL
from django.utils.log                  import logger

#TODO
@login_required
def create_technology(request):
    redirecturl = request.REQUEST.get('next','')
    jobs = Job.objects.all()
    return render_to_response('create_technology.html', {
        'jobs':jobs,'redirecturl':redirecturl,
    }, context_instance=RequestContext(request))

@login_required
def view_technology(request,technology_id):
    redirecturl = request.REQUEST.get('next','')
    technology = Technology.objects.get(id=technology_id)
    return render_to_response('view_technology.html', {
        'technology':technology,'redirecturl':redirecturl,
    }, context_instance=RequestContext(request))

@login_required
def edit_technology(request,technology_id):
    redirecturl = request.REQUEST.get('next','')
    technology = Technology.objects.get(id=technology_id)
    jobs = Job.objects.all()
    return render_to_response('edit_technology.html', {
        'jobs':jobs,'technology':technology,'redirecturl':redirecturl,
    }, context_instance=RequestContext(request))

def operation_groups_verification(result,msg,operation_groups_values):
    orders = []
    for operation_groups in operation_groups_values:
        try:
            gx_gxh = int(operation_groups['GX_GXH'])
        except:
            gx_gxh = None
            result = 1
            msg = str(unicode(_("please fill operation group order")))
            break
        orders.append(gx_gxh)
        try:
            gx_gz = int(operation_groups['GX_GZ'])
        except:
            gx_gz = None
            result = 1
            msg = str(unicode(_("please fill operation group job")))
            break
        gx_gxmc = operation_groups['GX_GXMC']

        try:
            job = Job.objects.get(id=gx_gz)
        except:
            result = 1
            msg = str(_("operation_group %d : %s, job not found") % (gx_gxh, gx_gxmc))
            break
    orders.sort()
    if not orders:
        result = 1
        msg = str(unicode(_("please add operation group")))
    elif orders and orders != range(orders[0],orders[-1]+1):
        result = 1
        msg = str(unicode(_("operation group orders is not sorted")))

    return result,msg

@login_required
def ajax_create_technology_verification(request):
    result = 0
    msg = ''
    if request.method == 'POST':
        technology_value_str        = request.POST.get('technology_value_str', False)
        operation_groups_value_str  = request.POST.get('operation_groups_value_str', False)
        technology_values           = json.loads(technology_value_str) if technology_value_str else []
        operation_groups_values     = json.loads(operation_groups_value_str) if operation_groups_value_str else []
        
        #find product_name
        product_cad_code = technology_values['product_cad_code'] if 'product_cad_code' in technology_values.keys() else None
        try:
            product = Product.objects.get(cad_code=product_cad_code)
        except:
            product = None
            result = 1
            msg = str(_("product %s is not found") % (product_cad_code))

        if product and Technology.objects.filter(product=product):
            result = 1
            msg = str(_("technology %s is already exist") % (product_cad_code))

        result,msg = operation_groups_verification(result,msg,operation_groups_values)

    data = {'result':result,'msg':msg}
    return HttpResponse('yuankong(' + json.dumps(data) + ');', content_type="application/json")

@login_required
def ajax_create_technology(request):
    result = 0
    msg = ''
    if request.method == 'POST':
        technology_value_str        = request.POST.get('technology_value_str', False)
        operation_groups_value_str  = request.POST.get('operation_groups_value_str', False)
        technology_values           = json.loads(technology_value_str) if technology_value_str else []
        operation_groups_values     = json.loads(operation_groups_value_str) if operation_groups_value_str else []
        
        product_cad_code = technology_values['product_cad_code'] if 'product_cad_code' in technology_values.keys() else None
        product = Product.objects.get(cad_code=product_cad_code)
        
        technology = Technology.objects.create(
            name                       = product.symbol,
            code                       = product.cad_code,
            product                    = product,
            file_code                  = technology_values['file_code'],
            publish_code               = technology_values['publish_code'],
            each_product               = technology_values['LGSL_MGLJ'],
            spare_part                 = technology_values['LGSL_BJ'],
            total                      = technology_values['LGSL_ZJ'],
            one_piece                  = technology_values['LGZL_DJ'],
            complete_set               = technology_values['LGZL_QT'],
            workblank_mark             = technology_values['workblank_mark'],
            workblank_standard_code    = technology_values['workblank_standard_code'],
            workblank_hardness         = technology_values['workblank_hardness'],
            workblank_species          = technology_values['workblank_species'],
            workblank_sectional_dimensions = technology_values['workblank_sectional_dimensions'],
            workblank_length           = technology_values['workblank_length'],
            workblank_quantity         = technology_values['workblank_quantity'],
            workblank_single_weight_kg = technology_values['workblank_single_weight_kg'],
            workblank_full_weight_kg   = technology_values['workblank_full_weight_kg'],
        )

        for operation_groups in operation_groups_values:
            job = Job.objects.get(id=int(operation_groups['GX_GZ']))
            operation_group = OperationGroup.objects.create(
                technology    = technology,
                order         = int(operation_groups['GX_GXH']),
                name          = operation_groups['GX_GXMC'],
                Job           = job
            )

    data = {'result':result,'msg':msg,'technology_id':technology.id}
    return HttpResponse('yuankong(' + json.dumps(data) + ');', content_type="application/json")

@login_required
def ajax_edit_technology_verification(request):
    result = 0
    msg = ''
    if request.method == 'POST':
        technology_value_str        = request.POST.get('technology_value_str', False)
        operation_groups_value_str  = request.POST.get('operation_groups_value_str', False)
        technology_values           = json.loads(technology_value_str) if technology_value_str else []
        operation_groups_values     = json.loads(operation_groups_value_str) if operation_groups_value_str else []
        
        #find product_name
        product_cad_code = technology_values['product_cad_code'] if 'product_cad_code' in technology_values.keys() else None
        try:
            product = Product.objects.get(cad_code=product_cad_code)
        except:
            product = None
            result = 1
            msg = str(_("product %s is not found") % (product_cad_code))

        result,msg = operation_groups_verification(result,msg,operation_groups_values)

    data = {'result':result,'msg':msg}
    return HttpResponse('yuankong(' + json.dumps(data) + ');', content_type="application/json")

@login_required
def ajax_edit_technology(request,technology_id):
    result = 0
    msg = ''
    if request.method == 'POST':
        technology_value_str        = request.POST.get('technology_value_str', False)
        operation_groups_value_str  = request.POST.get('operation_groups_value_str', False)
        technology_values           = json.loads(technology_value_str) if technology_value_str else []
        operation_groups_values     = json.loads(operation_groups_value_str) if operation_groups_value_str else []

        product_cad_code = technology_values['product_cad_code'] if 'product_cad_code' in technology_values.keys() else None
        product = Product.objects.get(cad_code=product_cad_code)
        
        technology = Technology.objects.get(id=technology_id)
        technology.name                       = product.symbol
        technology.code                       = product.cad_code
        technology.product                    = product
        technology.file_code                  = technology_values['file_code']
        technology.publish_code               = technology_values['publish_code']
        technology.each_product               = technology_values['LGSL_MGLJ']
        technology.spare_part                 = technology_values['LGSL_BJ']
        technology.total                      = technology_values['LGSL_ZJ']
        technology.one_piece                  = technology_values['LGZL_DJ']
        technology.complete_set               = technology_values['LGZL_QT']
        technology.workblank_mark             = technology_values['workblank_mark']
        technology.workblank_standard_code    = technology_values['workblank_standard_code']
        technology.workblank_hardness         = technology_values['workblank_hardness']
        technology.workblank_species          = technology_values['workblank_species']
        technology.workblank_sectional_dimensions = technology_values['workblank_sectional_dimensions']
        technology.workblank_length           = technology_values['workblank_length']
        technology.workblank_quantity         = technology_values['workblank_quantity']
        technology.workblank_single_weight_kg = technology_values['workblank_single_weight_kg']
        technology.workblank_full_weight_kg   = technology_values['workblank_full_weight_kg']
        technology.save()

        #-----------------------------------------------------------------------
        # 1.删除数据
        # 原有数据
        old_og_id_list = list(technology.operation_groups.all().values_list('id',flat=True))
        # 新数据
        new_og_id_list = [int(d.get('GX_ID')) for d in operation_groups_values if d.get('GX_ID').strip() != '']
        # 需要删除的数据
        og_del_id_list = list(set(old_og_id_list)^set(new_og_id_list))
        for og_id in og_del_id_list:
            og = OperationGroup.objects.get(id=og_id)
            # 删除对应的文件, 如果有的话
            TU1_file = og.TU1_file
            TU2_file = og.TU2_file
            TU3_file = og.TU3_file
            if TU1_file:
                TU1_file.set_file_to_delete()
            if TU2_file:
                TU2_file.set_file_to_delete()
            if TU3_file:
                TU3_file.set_file_to_delete()
            og.delete()

        #-----------------------------------------------------------------------
        # 2. 更新数据
        operation_groups_values = sorted(operation_groups_values,key=lambda d:d.get('GX_GXH'),reverse=False)
        for item in operation_groups_values:
            og_id = item.get('GX_ID')
            order = item.get('GX_GXH')
            name=item.get('GX_GXMC')
            job = Job.objects.get(id=int(item.get('GX_GZ')))
            # 新建工序
            if og_id.strip() == '':
                og = OperationGroup.objects.create(
                    Job=job,
                    technology=technology,
                    name=name,
                    order=order,
                )
            else:
                og = OperationGroup.objects.get(id=og_id)
                og.Job    = job
                og.name   = name
                og.order  = order
                og.save()

    data = {'result':result,'msg':msg}
    return HttpResponse('yuankong(' + json.dumps(data) + ');', content_type="application/json")

@login_required
def create_operation_group(request,operation_group_id):
    redirecturl = request.REQUEST.get('next','')
    operation_group = OperationGroup.objects.get(id=operation_group_id)
    devices = Device.objects.filter(prefix='KCSK')
    return render_to_response('create_operation_group.html', {
        'devices':devices,'operation_group':operation_group,
        'redirecturl':redirecturl,
    }, context_instance=RequestContext(request))

@login_required
def view_operation_group(request,operation_group_id):
    redirecturl = request.REQUEST.get('next','')
    operation_group = OperationGroup.objects.get(id=operation_group_id)
    return render_to_response('view_operation_group.html', {
        'operation_group':operation_group,'redirecturl':redirecturl,
        'UPLOAD_URL':UPLOAD_URL,
    }, context_instance=RequestContext(request))

@login_required
def edit_operation_group(request,operation_group_id):
    redirecturl = request.REQUEST.get('next','')
    operation_group = OperationGroup.objects.get(id=operation_group_id)
    og_content_type = ContentType.objects.get_for_model(operation_group)
    devices = Device.objects.filter(prefix='KCSK')
    return render_to_response('edit_operation_group.html', {
        'devices':devices,'operation_group':operation_group,
        'redirecturl':redirecturl,
        'content_type':og_content_type,
        'UPLOAD_URL':UPLOAD_URL,
    }, context_instance=RequestContext(request))

def operations_verification(result,msg,operations_values):
    orders = []
    for operations in operations_values:
        try:
            gb_gbh = int(operations['GB_GBH'])
        except:
            gb_gbh = None
            result = 1
            msg = str(unicode(_("please fill operation order")))
            break
        orders.append(gb_gbh)
    orders.sort()
    if not orders:
        result = 1
        msg = str(unicode(_("please add operation")))
    elif orders and orders != range(orders[0],orders[-1]+1):
        result = 1
        msg = str(unicode(_("operation orders is not sorted")))

    return result,msg

@login_required
def ajax_create_operation_group_verification(request):
    result = 0
    msg = ''
    if request.method == 'POST':
        operation_group_value_str   = request.POST.get('operation_group_value_str', False)
        operations_value_str        = request.POST.get('operations_value_str', False)
        operation_group_values      = json.loads(operation_group_value_str) if operation_group_value_str else []
        operations_values           = json.loads(operations_value_str) if operations_value_str else []
        
        #find device
        device_id = operation_group_values['device_type'] if 'device_type' in operation_group_values.keys() else None
        try:
            device = Device.objects.get(id=int(device_id))
        except:
            device = None
            result = 1
            msg = str(unicode(_("device is not found")))

        result,msg = operations_verification(result,msg,operations_values)

    data = {'result':result,'msg':msg}
    return HttpResponse('yuankong(' + json.dumps(data) + ');', content_type="application/json")

@login_required
def ajax_create_operation_group(request,operation_group_id):
    operation_group = OperationGroup.objects.get(id=operation_group_id)
    result = 0
    msg = ''
    if request.method == 'POST':
        operation_group_value_str   = request.POST.get('operation_group_value_str', False)
        operations_value_str        = request.POST.get('operations_value_str', False)
        operation_group_values      = json.loads(operation_group_value_str) if operation_group_value_str else []
        operations_values           = json.loads(operations_value_str) if operations_value_str else []
        
        device = Device.objects.get(id=int(operation_group_values['device_type']))

        operation_group.device        = device
        operation_group.coolant       = operation_group_values['coolant']
        operation_group.material_mark = operation_group_values['material_mark']
        operation_group.fixture       = operation_group_values['fixture']
        operation_group.save()

        for operations in operations_values:
            operation = Operation.objects.create(
                operation_group = operation_group,
                order       = int(operations['GB_GBH']),
                name        = operations['GB_GBM'],
                description = operations['GB_GBNR'],
                equipment   = operations['GB_GYZB']
            )

    data = {'result':result,'msg':msg}
    return HttpResponse('yuankong(' + json.dumps(data) + ');', content_type="application/json")

@login_required
def ajax_edit_operation_group_verification(request):
    result = 0
    msg = ''
    if request.method == 'POST':
        operation_group_value_str   = request.POST.get('operation_group_value_str', False)
        operations_value_str        = request.POST.get('operations_value_str', False)
        operation_group_values      = json.loads(operation_group_value_str) if operation_group_value_str else []
        operations_values           = json.loads(operations_value_str) if operations_value_str else []
        
        #find device
        device_id = operation_group_values['device_type'] if 'device_type' in operation_group_values.keys() else None
        try:
            device = Device.objects.get(id=int(device_id))
        except:
            device = None
            result = 1
            msg = str(unicode(_("device is not found")))

        result,msg = operations_verification(result,msg,operations_values)

    data = {'result':result,'msg':msg}
    return HttpResponse('yuankong(' + json.dumps(data) + ');', content_type="application/json")

@login_required
def ajax_edit_operation_group(request,operation_group_id):
    operation_group = OperationGroup.objects.get(id=operation_group_id)
    result = 0
    msg = ''
    if request.method == 'POST':
        operation_group_value_str   = request.POST.get('operation_group_value_str', False)
        operations_value_str        = request.POST.get('operations_value_str', False)
        operation_group_values      = json.loads(operation_group_value_str) if operation_group_value_str else []
        operations_values           = json.loads(operations_value_str) if operations_value_str else []
        
        device = Device.objects.get(id=int(operation_group_values['device_type']))

        operation_group.device        = device
        operation_group.coolant       = operation_group_values['coolant']
        operation_group.material_mark = operation_group_values['material_mark']
        operation_group.fixture       = operation_group_values['fixture']
        operation_group.save()

        for operation in operation_group.operations.all():
            for operations in operations_values:
                if operation.order == int(operations['GB_GBH']):
                    operation.name = operations['GB_GBM']
                    operation.description = operations['GB_GBNR']
                    operation.equipment = operations['GB_GYZB']
                    operation.save()

    data = {'result':result,'msg':msg}
    return HttpResponse('yuankong(' + json.dumps(data) + ');', content_type="application/json")





@login_required
def ajax_technology_update_reversion(request, technology_id):
    from copy import deepcopy
    result = 0
    msg = ''
    if request.method == 'POST':
        code = request.POST.get('code', None)
        note = request.POST.get('note', None)
        #create Technology
        technology = Technology.objects.get(id=technology_id)
        technology.status = 3
        technology.save()
        new_technology = deepcopy(technology)
        new_technology.id = None
        new_technology.workflow = None
        new_technology.status = 1
        new_technology.save()
        #create TechnologyRev
        TechnologyRev.objects.create(
            order       = technology.rev.all()[0].order+1 if technology.rev.all() else 2,
            parent      = technology,
            child       = new_technology,
            code        = code,
            note        = note,
            updated_by  = request.user
        )
        #create File for Technology
        content_type = ContentType.objects.get_for_model(technology)
        for fd in FileDirectory.objects.filter(is_active=True,content_type__id=content_type.id,object_id=technology.id):
            new_fd = deepcopy(fd)
            new_fd.id = None
            new_fd.object_id = new_technology.id
            new_fd.save()
        #create OperationGroup
        for operation_group in technology.operation_groups.all():
            new_operation_group = deepcopy(operation_group)
            new_operation_group.id = None
            new_operation_group.technology = new_technology
            new_operation_group.save()
            #create File for OperationGroup
            content_type = ContentType.objects.get_for_model(operation_group)
            for fd in FileDirectory.objects.filter(is_active=True,content_type__id=content_type.id,object_id=operation_group.id):
                new_fd = deepcopy(fd)
                new_fd.id = None
                new_fd.object_id = new_operation_group.id
                new_fd.save()
            #create Operation
            for operation in operation_group.operations.all():
                new_operation = deepcopy(operation)
                new_operation.id = None
                new_operation.operation_group = new_operation_group
                new_operation.state = None
                new_operation.save()
                #create OperationAttribute
                for operation_attribute in operation.operation_attributes.all():
                    new_operation_attribute = deepcopy(operation_attribute)
                    new_operation_attribute.id = None
                    new_operation_attribute.operation = new_operation
                    new_operation_attribute.save()
    data = {'result':result,'msg':msg}
    return HttpResponse(json.dumps(data), content_type="application/json")


def read_techlonogy_process_card(sh):
    '''
    get technology process card data

    return base technology info as dict and part operation_group data as list
    '''
    result_dict = {}   # 保存结果

    # 工艺名称
    technology_name = sh.row_values(1)[33]
    result_dict['technology_name'] = technology_name
    # 图号
    technology_code = sh.row_values(1)[33]
    result_dict['technology_code'] = technology_code
    # 工艺文件编号
    technology_file_code = sh.row_values(1)[52]
    result_dict['technology_file_code'] = technology_file_code
    # 发放号
    technology_publish_code = sh.row_values(1)[62]
    # 如果是浮点数，且小数点后面是0,则转为字符串
    if (type(technology_publish_code) == float) and (technology_publish_code - int(technology_publish_code) == 0):
        technology_publish_code = str(int(technology_publish_code))
    result_dict['technology_publish_code'] = technology_publish_code
    # 毛坯牌号
    workblank_mark = sh.row_values(6)[25]
    result_dict['workblank_mark'] = workblank_mark
    # 毛坯标准代号
    workblank_standard_code = sh.row_values(6)[32]
    result_dict['workblank_standard_code'] = workblank_standard_code
    # 毛坯硬度
    workblank_hardness = sh.row_values(6)[40]
    result_dict['workblank_hardness'] = workblank_hardness
    # 毛坯种类
    workblank_species = sh.row_values(6)[45]
    result_dict['workblank_species'] = workblank_species
    # 毛坯剖面尺寸
    workblank_sectional_dimensions = sh.row_values(6)[49]
    result_dict['workblank_sectional_dimensions'] = workblank_sectional_dimensions
    # 毛坯长度
    workblank_length = sh.row_values(6)[53]
    result_dict['workblank_length'] = workblank_length
    # 毛坯数量
    workblank_quantity = sh.row_values(6)[55]
    result_dict['workblank_quantity'] = workblank_quantity
    # 单件质量kg
    workblank_single_weight_kg = sh.row_values(6)[57]
    result_dict['workblank_single_weight_kg'] = workblank_single_weight_kg
    # 全套质量 kg
    workblank_full_weight_kg = sh.row_values(6)[62]
    result_dict['workblank_full_weight_kg'] = workblank_full_weight_kg

    # 判断表格中是否包含了 `牌号` 和 `材料`
    if sh.row_values(5)[25] == u'牌号' and sh.row_values(4)[25].replace(" ","") == u'材料':
        t_file_version = 0.2
    else:
        t_file_version = 0
    result_dict['t_file_version'] = t_file_version

    # 所有工序
    operation_groups_list = []
    start_row = 8               # 起始行, 9-1
    max_rows = sh.nrows         # 总行数
    end_row = max_rows - 5      # 结束行为倒数第5行
    # 第一组工序
    # 直接读取数据,如果数据为空,就跳过不存储
    for current_row in range(start_row,end_row):
        order = sh.row_values(current_row)[0]
        if type(order) != float:
            break
        d = {}
        d['order'] = int(order)                           # 工序号
        d['position_name'] = sh.row_values(current_row)[6]    # 工序名称
        d['name_cell'] = sh.row_values(current_row)[12]      # 工种
        # device_type
        operation_groups_list.append(d)
    # 第二组工序
    for current_row in range(start_row,end_row):
        order = sh.row_values(current_row)[23]
        if type(order) != float:
            break
        d = {}
        d['order'] = int(order)                                # 工序号
        d['position_name'] = sh.row_values(current_row)[29]    # 工序名称
        d['name_cell'] = sh.row_values(current_row)[35]        # 工种
        # device_type
        operation_groups_list.append(d)
    # 第三组工序
    for current_row in range(start_row,end_row):
        order = sh.row_values(current_row)[46]
        if type(order) != float:
            break
        d = {}
        d['order'] = int(order)                                # 工序号
        d['position_name'] = sh.row_values(current_row)[52]    # 工序名称
        d['name_cell'] = sh.row_values(current_row)[58]        # 工种
        # device_type
        operation_groups_list.append(d)

    # 将读取到的数据放入字典
    return result_dict,operation_groups_list

def read_techlonogy_process_extra_card(sheet):
    '''
    get extra technology process data
    return operation_group data list
    '''
    operation_groups_list = []
    start_row = 3  # 从0开始计数
    max_rows = sheet.nrows
    end_row = max_rows - 5
    # 第一组
    for current_row in range(start_row,end_row):
        order = sheet.row_values(current_row)[0]
        if type(order) != float:
            break
        d = {}
        d['order'] = int(order)                            # 工序号
        d['position_name'] = sheet.row_values(current_row)[6]    # 工种
        d['name_cell'] = sheet.row_values(current_row)[12].strip()       # 工序名称
        # device_type
        operation_groups_list.append(d)
    # 第二组
    for current_row in range(start_row,end_row):
        order = sheet.row_values(current_row)[23]
        if type(order) != float:
            break
        d = {}
        d['order'] = int(order)                            # 工序号
        d['position_name'] = sheet.row_values(current_row)[29]    # 工种
        d['name_cell'] = sheet.row_values(current_row)[35].strip()       # 工序名称
        # device_type
        operation_groups_list.append(d)
    # 第三组
    for current_row in range(start_row,end_row):
        order = sheet.row_values(current_row)[46]
        if type(order) != float:
            break
        d = {}
        d['order'] = int(order)                            # 工序号
        d['position_name'] = sheet.row_values(current_row)[52]    # 工种
        d['name_cell'] = sheet.row_values(current_row)[58].strip()       # 工序名称
        # device_type
        operation_groups_list.append(d)
    
    # 返回结果
    return operation_groups_list

def read_technology_picture_addition_card(sheet):
    '''
    get technology picture addition card data
    return operation_group data and operation data as list
    '''
    result_list = []
    temp_dict = {}
    # 读取工序号
    operation_group_order = sheet.row_values(1)[12]
    # 读取设备编号
    device_type = sheet.row_values(3)[12]
    # 冷却液
    coolant = sheet.row_values(5)[12]
    # 材料牌号
    material_mark = sheet.row_values(7)[12]
    # 夹具
    fixture = sheet.row_values(9)[12]
    # 工序名称
    operation_group_name = sheet.row_values(1)[13]
    # 取出原有的数据(一个字典)
    # temp_dict = filter(lambda d:d.get('order')==operation_group_order,operation_groups_list)[0]
    temp_dict['device_type'] = device_type
    temp_dict['coolant'] = coolant
    temp_dict['material_mark'] = material_mark
    temp_dict['fixture'] = fixture
    temp_dict['order'] = int(operation_group_order)
    temp_dict['operation_group_name'] = operation_group_name.strip()
    # 读取所有工步,一直往下读
    # 工步起始行(从 0 开始计数)
    operation_result_list = []
    operation_start_row = 16               # 起始行
    total_rows = sheet.nrows               # 总行数
    operation_end_row = total_rows - 5     # 结束行
    # 读取工步的每一行数据
    for row in range(operation_start_row,operation_end_row):
        tt_dict = {}
        # 工步号
        operation_order = sheet.row_values(row)[0]
        if type(operation_order) != float:
            break
        # 工步名称及内容
        operation_content = sheet.row_values(row)[1]
        # 工艺设备
        technology_device = sheet.row_values(row)[12]
        # 保存数据到 list
        tt_dict['operation_order'] = int(operation_order)
        tt_dict['operation_content'] = operation_content
        tt_dict['technology_device'] = technology_device
        operation_result_list.append(tt_dict)
    temp_dict['operations'] = operation_result_list
    result_list.append(temp_dict)
    return result_list

@login_required
def technology_excel_import(request):
    import xlrd
    from productcatalog.models import Product
    from person.models import Job
    from device.models import Device
    result = 0
    false_objects = []
    def deletelastchar(str_content):
        str_content = unicode(str_content)
        return str_content[:-2] if str_content.endswith('.0') else str_content

    if request.method == 'POST':
        # 获得上传的文件
        upload_file = request.FILES['file']
        work_book = None
        try:
            work_book = xlrd.open_workbook(file_contents=upload_file.read())
        except Exception, e:
            false_objects.append(str(e))
            return render_to_response('technology_excel_import.html', {
                    'redirecturl':request.REQUEST.get('next',''), 
                    'false_objects':false_objects,
                }, context_instance=RequestContext(request))

        #-----------------------------------------------------------------------
        # logger.info(u'starting read file....')
        sh = work_book.sheet_by_index(0)
        # logger.info(u'get data from first sheet....')
        # 读取第一个 sheet 的工艺和工序数据
        # gy_data_dict 形如 {'a':a,'b':b,'c':c}
        # gx_data_list 形如 [{'a':a,'b':b,'c':c},{'a':a,'b':b,'c':c},{'a':a,'b':b,'c':c}]
        gy_data_dict,gx_data_list = read_techlonogy_process_card(sh)
        # 保存工序的 list, 是第一个 sheet 和后面 sheet 的工序的总和
        gx_result_list = gx_data_list
        # 保存工序及其公布的 list
        # 形如 [{'a':a,'b':b,[]},{'a':a,'b':b,[]},{'a':a,'b':b,[]}]
        gx_with_gb_list = []
        # 从第二页开始读其他数据
        sheet_start_index = 1
        # sheet 总数
        total_sheets = work_book.nsheets
        for sheet_index in range(sheet_start_index,total_sheets):
            sh = work_book.sheet_by_index(sheet_index)
            sheet_type_gygck = sh.row_values(0)[11].replace(" ",'')
            sheet_type_gyftk = sh.row_values(0)[3].replace(" ","")
            if sheet_type_gygck == u'机械加工工艺过程卡':
                extra_data = read_techlonogy_process_extra_card(sh)
                gx_result_list = gx_result_list + extra_data
            elif sheet_type_gyftk == u'工艺附图卡片':
                # 工序及其工步
                operation_groups_data_dict = read_technology_picture_addition_card(sh)
                gx_with_gb_list = gx_with_gb_list + operation_groups_data_dict
            else:
                false_objects.append(_("unknow sheet %(sheet_index)s type") %{
                    'sheet_index':sheet_index+1,
                })
                return render_to_response('technology_excel_import.html', {
                    'redirecturl':request.REQUEST.get('next',''), 
                    'false_objects':false_objects,
                }, context_instance=RequestContext(request))

        # 数据长度
        gx_result_list_count = len(gx_result_list)
        gx_with_gb_count = len(gx_with_gb_list)

        #-----------------------------------------------------------------------
        # 合并数据
        operation_group_list = []
        for item in gx_result_list:
            temp_dict = {}
            order = item.get('order')
            gx_with_gb_item = filter(lambda d:d.get('order') == order,gx_with_gb_list)[0]
            temp_dict['order'] = order
            temp_dict['name_cell'] = item.get('name_cell')
            temp_dict['position_name'] = item.get('position_name')
            temp_dict['operation_group_name'] = gx_with_gb_item.get('operation_group_name')
            temp_dict['device_type'] = gx_with_gb_item.get('device_type')
            temp_dict['fixture'] = gx_with_gb_item.get('fixture')
            temp_dict['coolant'] = gx_with_gb_item.get('coolant')
            temp_dict['material_mark'] = gx_with_gb_item.get('material_mark')
            temp_dict['operations'] = gx_with_gb_item.get('operations')
            operation_group_list.append(temp_dict)
        # logger.info('工艺基本信息')
        # logger.info(gy_data_dict)
        # logger.info('工序信息')
        # logger.info(gx_result_list)
        # logger.info('工序及其工步信息')
        # logger.info(operation_group_list)
        # return HttpResponseRedirect(request.META.get("HTTP_REFERER","/"))

        #-----------------------------------------------------------------------
        # 验证数据
        t_file_version = gy_data_dict.get('t_file_version')

        # 1. 工序数量不一致
        if gx_with_gb_count != gx_result_list_count:
            false_objects.append(_("number of technology picture addition card not equal number of operation group"))
            return render_to_response('technology_excel_import.html', {
                    'redirecturl':request.REQUEST.get('next',''), 
                    'false_objects':false_objects,
                }, context_instance=RequestContext(request))

        # 2. 验证 product 存在
        # logger.info(u'check product exists or not...')
        technology_code = gy_data_dict.get('technology_code')
        try:
            product = Product.objects.get(cad_code=technology_code)
        except Product.DoesNotExist:
            false_objects.append(_("product %s not exist") % (technology_code))
        # 3. 循环验证 postion 和 job 存在
        for item in operation_group_list:
            position_name = item.get('position_name')
            order = item.get('order')
            if not Position.objects.filter(name=position_name).exists() or not Job.objects.filter(position__name=position_name).exists():
                false_objects.append(_("postion/job does not exist for %(position_name)s which order is %(order)s in technology picture addition card") %{
                    "position_name" : position_name,
                    "order": order,
                })
            device_type = item.get('device_type')
            if not Device.objects.filter(type=device_type.strip()).exists():
                false_objects.append(_("device %(device_type)s which order is %(order)s in technology picture addition card,please contact the admin add it") %{
                    "device_type" : device_type,
                    "order": order,
                })
        # 4. 验证工序名称是否一致
        for item in operation_group_list:
            if item.get('operation_group_name') != item.get('name_cell'):
                false_objects.append(_("operation_group_name does not matched which order is %(order)s") %{
                    "order":item.get('order'),
                })
        if false_objects:
            return render_to_response('technology_excel_import.html', {
                'redirecturl':request.REQUEST.get('next',''), 
                'false_objects':false_objects,
            }, context_instance=RequestContext(request))

        # return HttpResponseRedirect(request.META.get("HTTP_REFERER","/"))
        #-----------------------------------------------------------------------
        # logger.info(u'starting create technology...')
        # 读取数据并创建

        technologies_queryset = Technology.objects.filter(product=product)
        # 更新现有工艺或创建新工艺
        if technologies_queryset:
            technology = technologies_queryset[0]
            if technology.technology_workflow_status != 0:
                false_objects.append(_("the technology is already exist, and started technology workflow, you donot edit it"))
                return render_to_response('technology_excel_import.html', {
                    'redirecturl':request.REQUEST.get('next',''), 
                    'false_objects':false_objects,
                }, context_instance=RequestContext(request))

            #update technology
            technologies_queryset.update(
                name                            = gy_data_dict.get('technology_name'),
                code                            = gy_data_dict.get('technology_code'),
                product                         = product,
                file_code                       = gy_data_dict.get('technology_file_code'),
                publish_code                    = gy_data_dict.get('technology_publish_code'),
                workblank_mark                  = gy_data_dict.get('workblank_mark'),
                workblank_standard_code         = gy_data_dict.get('workblank_standard_code'),
                workblank_hardness              = gy_data_dict.get('workblank_hardness'),
                workblank_species               = gy_data_dict.get('workblank_species'),
                workblank_sectional_dimensions  = gy_data_dict.get('workblank_sectional_dimensions'),
                workblank_length                = gy_data_dict.get('workblank_length'),
                workblank_quantity              = gy_data_dict.get('workblank_quantity'),
                workblank_single_weight_kg      = gy_data_dict.get('workblank_single_weight_kg'),
                workblank_full_weight_kg        = gy_data_dict.get('workblank_full_weight_kg'),
            )
        else:
            technology = Technology.objects.create(
                name                            = gy_data_dict.get('technology_name'),
                code                            = gy_data_dict.get('technology_code'),
                product                         = product,
                file_code                       = gy_data_dict.get('technology_file_code'),
                publish_code                    = gy_data_dict.get('technology_publish_code'),
                workblank_mark                  = gy_data_dict.get('workblank_mark'),
                workblank_standard_code         = gy_data_dict.get('workblank_standard_code'),
                workblank_hardness              = gy_data_dict.get('workblank_hardness'),
                workblank_species               = gy_data_dict.get('workblank_species'),
                workblank_sectional_dimensions  = gy_data_dict.get('workblank_sectional_dimensions'),
                workblank_length                = gy_data_dict.get('workblank_length'),
                workblank_quantity              = gy_data_dict.get('workblank_quantity'),
                workblank_single_weight_kg      = gy_data_dict.get('workblank_single_weight_kg'),
                workblank_full_weight_kg        = gy_data_dict.get('workblank_full_weight_kg'),
            )

        #-----------------------------------------------------------------------
        # 更新工序或创建工序
        for operation_group_item in operation_group_list:
            # 工序序号
            operation_group_order = operation_group_item.get('order')
            # logger.info(u'开始创建工序{0}...'.format(operation_group_order))
            name = operation_group_item.get('name_cell')
            job = Job.objects.get(position__name=operation_group_item.get('position_name'))

            try:
                device = Device.objects.get(type=operation_group_item.get('device_type'))
            except Exception, e:
                device = None
            # 如果工序已存在,则更新工序,如果不存在,则创建
            operation_groups_queryset = OperationGroup.objects.filter(
                        technology=technology,
                        order=operation_group_order)
            # 创建或更新
            if operation_groups_queryset:
                # 更新工序
                operation_groups_queryset.update(
                    name            = name,
                    device          = device,
                    Job             = job,
                    coolant         = operation_group_item.get('coolant'),
                    material_mark   = operation_group_item.get('material_mark'),
                    fixture         = operation_group_item.get('fixture'),
                )
                operation_group = operation_groups_queryset[0]
            # 创建
            else:
                operation_group = OperationGroup.objects.create(
                    technology    = technology,
                    order         = operation_group_order,
                    name          = name,
                    device        = device,
                    Job           = job,
                    coolant       = operation_group_item.get('coolant'),
                    material_mark = operation_group_item.get('material_mark'),
                    fixture       = operation_group_item.get('fixture'),
                )

            # logger.info(u'创建工序结束')
            #-------------------------------------------------------------------
            # 创建或更新工步
            # logger.info(u'开始创建工步')
            # 之前保存的工步数据
            operations_data_list = operation_group_item.get('operations')
            for operation_item in operations_data_list:
                # 工步序号
                operation_order = operation_item.get('operation_order')
                # name (程序使用,设置为和 order 一样)
                operation_name = str(operation_order)
                # 工艺设备
                technology_device = operation_item.get('technology_device')
                # 工步名称及内容
                operation_content = operation_item.get('operation_content')

                # 工序名称
                operation_group_name = operation_group.name
                if operation_group_name.find(u'时效') > 0:
                    # 读取小时之前的数字
                    m = re.search(ur'\d+(?=小时)',operation_content)
                    # 如果读取到值,就设置为时效
                    if m:
                        period = int(m.group())
                    # 如果读取不到,则设置为 0
                    else:
                        period = 0
                    operation_type = OperationType.objects.get(name=u'时效')
                else:
                    period = None
                    operation_type = OperationType.objects.get(name=u'普通')

                # 如果检测到 operation_content 包含数字，则可能需要用户添加工步属性
                if re.search(r'\d+',operation_content):
                    need_attribute = 2   # maybe
                else:
                    need_attribute = 1   # not requried

                # 更新或创建工步
                operations_queryset = Operation.objects.filter(operation_group=operation_group,order=operation_order)
                if operations_queryset:
                    operations_queryset.update(
                        name             = operation_name,
                        description      = operation_content,
                        equipment        = technology_device,
                        period           = period,
                        operation_type   = operation_type,
                        need_attribute   = need_attribute,
                    )
                    operation = operations_queryset[0]
                else:
                    operation = Operation.objects.create(
                        operation_group  = operation_group,
                        order            = operation_order,
                        name             = operation_name,                      # ok
                        description      = operation_content,                   # ok
                        equipment        = technology_device,                   # ok
                        period           = period,
                        operation_type   = operation_type,
                        need_attribute   = need_attribute,
                    )
            # logger.info(u'工步创建结束')

        # logger.info(u'technology import finished...')

        # 如果成功了,则跳转到 view_technology
        # 如果失败了,则提示用户
        if false_objects:
            return render_to_response('technology_excel_import.html', {
                    'redirecturl':request.REQUEST.get('next',''), 
                    'false_objects':false_objects,
            }, context_instance=RequestContext(request))
        else:
            redirecturl = reverse('view_technology',args=[technology.id])
            return HttpResponseRedirect(redirecturl)

    return render_to_response('technology_excel_import.html', {
        'redirecturl':request.REQUEST.get('next',''), 'false_objects':false_objects,
    }, context_instance=RequestContext(request))
    
@login_required
def technology_files_list(request,technology_id):
    technology = Technology.objects.get(id = technology_id)
    fileowner_type = ContentType.objects.get_for_model(technology)
    
    files = File.objects.filter(content_type__pk=fileowner_type.id,object_id=technology.id)
    return render_to_response('technology_files.html', {
        'technology':technology,'contenttype_id':fileowner_type.id,'files':files,
    }, context_instance=RequestContext(request))
    
@login_required
def operation_group_files_list(request,operation_group_id):
    operation_group = OperationGroup.objects.get(id = operation_group_id)
    fileowner_type = ContentType.objects.get_for_model(operation_group)
    
    return render_to_response('operation_group_files.html', {
        'operation_group':operation_group,'contenttype_id':fileowner_type.id
    }, context_instance=RequestContext(request))
    
# @login_required
def technologies_list(request):
    technologies = Technology.objects.all()
    form  = TechnologyRevForm()

    # 工艺模板文件下载地址
    technology_template_xls_url = TECHNOLOGY_TEMPLATE_LATEST_URL

    return render_to_response('technologies_list.html', {
        'technologies':technologies,'form':form,
        'technology_template_xls_url':technology_template_xls_url,
    }, context_instance=RequestContext(request))
    
@login_required
def technology_states_list(request,technology_id):
    technology = Technology.objects.get(id=technology_id)
    operation_groups_list = []
    operation_groups = technology.operation_groups.all()
    for count in range((operation_groups.count()+4-1)/4):
        operation_groups_list.append(operation_groups[count*4:(count+1)*4])
    return render_to_response('technology_states_list.html', {
        'technology':technology,'operation_groups_list':operation_groups_list
    }, context_instance=RequestContext(request))
    
@login_required
def technology_workflow(request,technology_id):
    redirecturl = request.REQUEST.get('next','')
    if request.user.has_perm('technologies.show_technology_workflow'):
        technology = Technology.objects.get(id=technology_id)
        content_type = ContentType.objects.get_for_model(technology)
        approve_permission = False
        refusal_permission = False
        if get_allowed_transitions(technology,request.user):
            if has_permission(technology,request.user,"check"):
                approve_permission = True
                if get_workflow(technology).initial_state != get_state(technology):
                    refusal_permission = True

        return render_to_response('technology_workflow.html', {
            'object':technology,'content_type':content_type,'redirecturl':redirecturl,
            'approve_permission':approve_permission,'refusal_permission':refusal_permission,
        }, context_instance=RequestContext(request))

@login_required
def ajax_init_workflow(request):
    result = 0
    technology_id = int(request.POST.get('technology_id'))
    technology = Technology.objects.get(id=technology_id)
    #set workflow
    workflow = Workflow.objects.create(name=technology.name)
    technology.workflow = workflow
    technology.save()
    #set state
    pre_state = None
    for operation_group in technology.operation_groups.all().order_by('order'):
        for operation in operation_group.operations.all().order_by('order'):
            #create state
            state = State.objects.create(name=operation.name, workflow=workflow)
            operation.state = state
            operation.save()
            #create transition
            transition = Transition.objects.create(
                name         = "Make "+state.name, 
                workflow     = workflow, 
                destination  = state
            )
            transition.save()
            #set initial_state
            if operation_group.order == 1 and operation.order == 1:
                workflow.initial_state = state
                workflow.save()
                pre_state = state
            elif pre_state:
                #set transition
                pre_state.transitions.add(transition)
                pre_state.save()
                pre_state = state

            # #create Semifinished Product
            # operation.product = create_semifinished_product(operation)
            # operation.save()

    data = {'result':result,'msg':'error'}
    return HttpResponse('yuankong(' + json.dumps(data) + ');', content_type="application/json")

#util to create Semifinished Product
def create_semifinished_product(operation):
    from productcatalog.models import Category
    from productcatalog.models import Product, ProductAttribute
    #TODO:get category
    category = Category.objects.get(id=1)
    products = Product.objects.filter(cad_code=operation.operation_group.technology.product.cad_code+'%03d'%operation.order+'%03d'%operation.operation_group.order)
    if products:
        product = products[0]
    else:
        product = Product()
    product.cad_code    = operation.operation_group.technology.product.cad_code+'%03d'%operation.order+'%03d'%operation.operation_group.order
    product.category  = category
    product.name      = _('BAN')+operation.operation_group.technology.product.cad_code+'%03d'%operation.operation_group.order
    product.type      = 2
    product.save()

    for operation_attribute in operation.operation_attributes.all():
        product_attributes = ProductAttribute.objects.filter(product=operation.product,attribute=operation_attribute.attribute)
        if product_attributes:
            product_attribute = product_attributes[0]
        else:
            product_attribute = ProductAttribute()
        product_attribute.product        = product
        product_attribute.attribute      = operation_attribute.attribute
        product_attribute.display_value  = operation_attribute.display_value
        product_attribute.absolute_value = operation_attribute.absolute_value
        product_attribute.is_published   = operation_attribute.is_published
        product_attribute.ext_code       = operation_attribute.ext_code
        product_attribute.difference     = operation_attribute.difference
        product_attribute.save()
    return product

#打算发起审核流程作成通用的ajax，有点复杂，先一放
@login_required
def ajax_start_object_workflow(request):
    result = 0
    msg = ''
    if request.user.has_perm(str_permission):
        content_type_id  = int(request.POST.get('content_type_id'))
        object_id        = int(request.POST.get('object_id'))
        workflow_name    = request.POST.get('workflow_name')

        content_type     = ContentType.objects.get_for_id(content_type_id)
        content_object   = content_type.get_object_for_this_type(pk=object_id)
        str_permission   = content_type.app_label+'start_workflow'
        workflow         = Workflow.objects.get(name=workflow_name)

        #set workflow
        set_workflow(content_object,workflow)

        #create state_details
        workflow_object_relation = WorkflowObjectRelation.objects.get(content_type__pk=content_type.id,content_id=content_object.id)
        states = State.objects.filter(workflow=workflow)
        for state in states:
            StateDetail.objects.get_or_create(workflow_object_relation=workflow_object_relation,state=state)

        #set initial_state state_details.status
        state_detail = content_object.state_detail
        state_detail.status = 0
        state_detail.save()

    data = {'result':result,'msg':msg,}
    return HttpResponse('yuankong(' + json.dumps(data) + ');', content_type="application/json")


@login_required
def technology_start_workflow(request,technology_id):
    if request.user.has_perm('technologies.start_technology_workflow'):
        technology      = Technology.objects.get(id=technology_id)
        content_type    = ContentType.objects.get_for_model(technology)
        workflow        = Workflow.objects.get(name='工艺审核流程')

        #permission for this workflow
        permission_check = Permission.objects.get(codename='check')
        WorkflowPermissionRelation.objects.get_or_create(workflow=workflow,permission=permission_check)

        role_jishu        = Role.objects.get(name='技术部')
        role_biaozhunhua  = Role.objects.get(name='质量部负责人')
        role_huiqian      = Role.objects.get(name='生产部负责人')
        role_pizhun       = Role.objects.get(name='技术部主管')
        
        state_bianzhi     = State.objects.get(name='编制')
        state_shenhe      = State.objects.get(name='审核')
        state_biaozhunhua = State.objects.get(name='标准化')
        state_huiqian     = State.objects.get(name='会签')
        state_pizhun      = State.objects.get(name='批准')

        StatePermissionRelation.objects.get_or_create(state=state_bianzhi,permission=permission_check,role=role_jishu)
        StatePermissionRelation.objects.get_or_create(state=state_shenhe,permission=permission_check,role=role_jishu)
        StatePermissionRelation.objects.get_or_create(state=state_biaozhunhua,permission=permission_check,role=role_biaozhunhua)
        StatePermissionRelation.objects.get_or_create(state=state_huiqian,permission=permission_check,role=role_huiqian)
        StatePermissionRelation.objects.get_or_create(state=state_pizhun,permission=permission_check,role=role_pizhun)
        
        #set workflow
        set_workflow(technology,workflow)
        #create state_details
        technology_type = ContentType.objects.get_for_model(technology)
        workflow_object_relation = WorkflowObjectRelation.objects.get(content_type__pk=technology_type.id,content_id=technology.id)
        states = State.objects.filter(workflow=workflow)
        for state in states:
            StateDetail.objects.get_or_create(workflow_object_relation=workflow_object_relation,state=state)

        #set initial_state state_details.status
        state_detail = technology.state_detail
        state_detail.status = 0
        state_detail.save()
        
        
    return HttpResponseRedirect(reverse('technologies_list'))

msg = {
    0:'success',
    1:'您没有权限执行这个操作',
    2:'这个审核流程已经做完，不能进行任何操作',
}

#这个函数已改为ContentType，可以通用
@login_required
def ajax_technology_workflow_approve(request,content_type_id,object_id):
    result = 0
    content_type = ContentType.objects.get_for_id(content_type_id)
    content_object = content_type.get_object_for_this_type(pk=object_id)
    if request.method == 'POST':
        transitions = get_allowed_transitions(content_object,request.user)
        if transitions:
            if has_permission(content_object,request.user,"check"):
                #set status
                state_detail = content_object.state_detail
                state_detail.status = 2
                state_detail.save()
                WorkflowLog.objects.create(
                    state_detail = state_detail,
                    executor     = request.user,
                    note         = request.POST['note'],
                    type         = 1,
                )
                #do_transition
                try:
                    do_transition(content_object,transitions[0],request.user)
                except:
                    pass
                #set current status
                state_detail = content_object.state_detail
                state_detail.status = 0
                state_detail.save()
            else:
                result = 1
        else:
            result = 2
        
    data = {'result':result,'msg':msg[result],}
    return HttpResponse('yuankong(' + json.dumps(data) + ');', content_type="application/json")

#这个函数已改为ContentType，可以通用
@login_required
def ajax_technology_workflow_refusal(request,content_type_id,object_id):
    result = 0
    content_type = ContentType.objects.get_for_id(content_type_id)
    content_object = content_type.get_object_for_this_type(pk=object_id)
    if request.method == 'POST' and get_allowed_transitions(content_object,request.user):
        current_state = get_state(content_object)
        transitions = Transition.objects.filter(destination=current_state)
        if transitions:
            if has_permission(content_object,request.user,"check"):
                #set status
                state_detail = content_object.state_detail
                state_detail.status = 1
                state_detail.save()
                WorkflowLog.objects.create(
                    state_detail = state_detail,
                    executor     = request.user,
                    note         = request.POST['note'],
                    type         = 2,
                )
                #do_transition
                for state in transitions[0].states.all():
                    try:
                        set_state(content_object,state)
                    except:
                        pass
                    #set current status
                    state_detail = content_object.state_detail
                    state_detail.status = 3
                    state_detail.save()
                    break
            else:
                result = 1
        else:
            result = 2

    data = {'result':result,'msg':msg[result],}
    return HttpResponse('yuankong(' + json.dumps(data) + ');', content_type="application/json")

def check_empty_error(sh, t_file_version):
    operation_group_start_row = 9
    if t_file_version == 0.2:
        cad_code = sh.row_values(1)[2]
        operation_start_col = 7
    else:
        cad_code = ''
        operation_start_col = 6
    if cad_code == '':
        return 'cad_code'
    while operation_group_start_row < sh.nrows and any(sh.row_values(operation_group_start_row)):
        order = sh.row_values(operation_group_start_row)[0]
        name_cell = sh.row_values(operation_group_start_row)[1]
        if order == '':
            return "operation_order"
        if name_cell == '':
            return 'operation_group_name'
        operation_group_start_row += 1
    return None


def check_fk_error(sh, t_file_version):
    operation_group_start_row = 9
    if t_file_version == 0.2:
        operation_start_col = 7
    else:
        operation_start_col = 6
    if not Product.objects.filter(cad_code=sh.row_values(1)[2]):
        return 'cad_code'
    while operation_group_start_row < sh.nrows and sh.row_values(operation_group_start_row)[0]\
     and sh.row_values(operation_group_start_row)[operation_start_col]:
        job_id = sh.row_values(operation_group_start_row)[2]
        device_type = sh.row_values(operation_group_start_row)[3]
        if job_id != '':
            try:
                job_id = int(job_id)
            except ValueError:
                return 'job_id'
            if not Job.objects.filter(id=job_id):
                return 'job_id'
        if not Device.objects.filter(type=device_type):
            return 'device_type'
        operation_group_start_row += 1
    return None


@login_required
def view_operation_attribute_needs(request,technology_id):
    ''' 查看工艺下所有需要创建属性的工步 '''
    technology = Technology.objects.get(id=technology_id)
    operations = technology.operations_attribute_needs

    return render(request,'view_operation_attribute_needs.html',{
        'technology':technology,
        'operations':operations,
    })
