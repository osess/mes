#-*- coding: UTF-8 -*- 
from django.shortcuts import render_to_response,render
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.contrib import auth
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ugettext
from django.utils.simplejson.encoder import JSONEncoder
from django.conf import settings
import json
import datetime
#from thirdparty
#from workflows.models import
from workflows.models import State
from workflows.utils import *
from permissions.utils import *
#from xxd
from yt_timesheet.models import Timesheet
from technologies.models import Technology, OperationGroup, Operation, OperationAttribute
from person.models import Employee
from warehouse.yt_views import applications_list
from notification.models import NoticeType
from notification.yt_views import *
#from lxy
from manufactureplan.models import *
from productcatalog.models import Attribute
#from device.models import DeviceItem
from warehouse.models import *
from warehouse.forms import BomEntryForm
# by recall
from apps.utils import get_object_or_none
from yt_log.models import StateDetail
from django.contrib import messages
from django.utils.log import logger

from .utils import productionline_do_transition,get_mis_id_list_other
from .utils import get_all_check_manu_items,get_all_wipe_burr_manu_items,get_all_heattreatment_manu_items,get_all_incasement_manu_items,get_all_period_manu_items
from .utils import get_batch_productionlines

@login_required
def ajax_update_mig_column(request, mig_id):
    mig = ManufactureItemGroup.objects.get(id=mig_id)
    result = 0
    msg = ""
    if request.method == 'GET':
        furnace_batch = request.GET.get("furnace_batch", None)
        mig.furnace_batch = furnace_batch
        mig.save()
        msg = mig.furnace_batch
            
    data   = {'result':result,'msg':msg}
    return HttpResponse(json.dumps(data), content_type="application/json")

@login_required
def working_productionlines_list(request):
    productionlines = [productionline for productionline in ProductionLine.objects.all() if get_workflow(productionline)]
    return render_to_response('working_productionlines_list.html', {
        'productionlines':productionlines,
        'l_m_manufacture_active':"active",
    }, context_instance=RequestContext(request))
    
@login_required
def productionlines_list(request):
    manufactureplans = [manufactureplan for manufactureplan in ManufacturePlan.objects.all().order_by('id') if manufactureplan.productionlines]
    return render_to_response('productionlines_list.html', {
        'manufactureplans':manufactureplans,
        'l_m_manufacture_active':"active",
    }, context_instance=RequestContext(request))

@login_required
def manufactureplan_workflow(request,manufactureplan_id):
    redirecturl = request.REQUEST.get('next','')
    manufactureplan = ManufacturePlan.objects.get(id=manufactureplan_id)
    content_type = ContentType.objects.get_for_model(manufactureplan)
    approve_permission = False
    refusal_permission = False
    if get_allowed_transitions(manufactureplan,request.user):
        if has_permission(manufactureplan,request.user,"check"):
            approve_permission = True
            if get_workflow(manufactureplan).initial_state != get_state(manufactureplan):
                refusal_permission = True

    return render_to_response('manufactureplan_workflow.html', {
        'object':manufactureplan,'content_type':content_type,'redirecturl':redirecturl,
        'approve_permission':approve_permission,'refusal_permission':refusal_permission,
        'content_type_id':content_type.id,'object_id':manufactureplan.id,
        'l_m_manufacture_active':"active",
    }, context_instance=RequestContext(request))

@login_required
def manufactureplan_start_workflow(request,manufactureplan_id):
    manufactureplan = ManufacturePlan.objects.get(id=manufactureplan_id)
    content_type    = ContentType.objects.get_for_model(manufactureplan)
    workflow        = Workflow.objects.get(name='生产通知单审核流程')

    #permission for this workflow
    permission_check = Permission.objects.get(codename='check')
    WorkflowPermissionRelation.objects.get_or_create(workflow=workflow,permission=permission_check)

    role_shichang     = Role.objects.get(name='市场部')
    role_jishu        = Role.objects.get(name='技术部')
    role_zhiliang     = Role.objects.get(name='质量部')
    role_shengchan    = Role.objects.get(name='生产部负责人')
    
    state_shichang    = State.objects.get(name='市场部')
    state_jishu       = State.objects.get(name='技术部')
    state_zhiliang    = State.objects.get(name='质量部')
    state_shengchan   = State.objects.get(name='生产部')

    StatePermissionRelation.objects.get_or_create(state=state_shichang,permission=permission_check,role=role_shichang)
    StatePermissionRelation.objects.get_or_create(state=state_jishu,permission=permission_check,role=role_jishu)
    StatePermissionRelation.objects.get_or_create(state=state_zhiliang,permission=permission_check,role=role_zhiliang)
    StatePermissionRelation.objects.get_or_create(state=state_shengchan,permission=permission_check,role=role_shengchan)
    
    #set workflow
    set_workflow(manufactureplan,workflow)

    #create state_details
    manufactureplan_type = ContentType.objects.get_for_model(manufactureplan)
    workflow_object_relation = WorkflowObjectRelation.objects.get(content_type__pk=manufactureplan_type.id,content_id=manufactureplan.id)
    states = State.objects.filter(workflow=workflow)
    for state in states:
        StateDetail.objects.get_or_create(workflow_object_relation=workflow_object_relation,state=state)

    #set initial_state state_details.status
    state_detail = manufactureplan.state_detail
    state_detail.status = 0
    state_detail.save()

    return HttpResponseRedirect(reverse('manufactureplan_workflow', kwargs={'manufactureplan_id':manufactureplan_id}) + "?next=/xadmin/manufactureplan/manufactureplan/")

@login_required
def adminx_create_new_productionline(request,manufactureplan_id):
    '''
    根据生产通知单,创建生产任务
    '''
    redirecturl = request.REQUEST.get('next','')
    manufactureplan = ManufacturePlan.objects.get(id=manufactureplan_id)
    for manu_item_group in manufactureplan.manu_item_groups.all():
        # 如果生产任务不存在,则创建
        if not manu_item_group.productionline:
            #find technology
            technology = manu_item_group.technology
            #create productionline
            production_line = create_new_productionline(technology,manu_item_group)
            manu_item_group.productionline = production_line
            manu_item_group.save()

            #send notice to warehouse
            group       = Group.objects.get(name="仓库")
            message     = _("You get a Warehouse Application with <a href='%s'> %s </a>") %(reverse(applications_list),manufactureplan)
            notice_type = NoticeType.objects.get(label="warehouse_application")
            notice_to_group(group,request.user,message,notice_type)

    return HttpResponseRedirect(redirecturl)

def create_new_productionline(technology, manu_item_group):
    if manu_item_group.productionline:
        logger.info('if....................................')
        manufactureplan = manu_item_group.manufactureplan
        #create new production_line
        #TODO:'%s%03d' %(now.strftime('%Y%m%d'),count+1)
        #productionlines_t = ProductionLine.objects.all()
        #productionlines_m = [MIG.productionline for MIG in manufactureplan.manu_item_groups.all()]
        production_line_new = ProductionLine.objects.create(
            #code          = manufactureplan.code + technology.code + str(len(productionlines_t)),
            #name          = manufactureplan.name + str(len(productionlines_m)),
            #start_time    = manufactureplan.start_time,
            #finish_time   = manufactureplan.finish_time,
            technology = technology
        )
        #create new oper_group_records
        # for operation_group in technology.operation_groups.all():
        for oper_group_record in manu_item_group.productionline.oper_group_records.all():
            #oper_group_records = OperationGroupRecord.objects.all()
            oper_group_record_new = OperationGroupRecord.objects.create(
                #code               = technology.code + str(operation_group.order) + str(len(oper_group_records)),
                #TODO
                #job_id                = 1,
                productionline  = production_line_new,
                operation_group = oper_group_record.operation_group
            )
            for device_item in oper_group_record.device_items.all():
                oper_group_record_new.device_items.add(device_item)
            # oper_group_record_new.save()
            #create new operation_records
            for operation in oper_group_record.operation_group.operations.all():
                #operation_records = OperationRecord.objects.all()
                operation_record_new = OperationRecord.objects.create(
                    #code                  = technology.code + str(operation_group.order) + str(operation.order) + str(len(operation_records)),
                    #TODO:
                    #employee_id           = 1,
                    oper_group_record = oper_group_record_new,
                    quantity          = manu_item_group.quantity,
                    operation         = operation
                )
    else:
        production_line_new = ProductionLine.objects.create(
            technology = technology
        )
        for operation_group in technology.operation_groups.all():
            oper_group_record_new = OperationGroupRecord.objects.create(
                productionline  = production_line_new,
                operation_group = operation_group
            )
            for operation in operation_group.operations.all():
                operation_record_new = OperationRecord.objects.create(
                    oper_group_record = oper_group_record_new,
                    quantity          = manu_item_group.quantity,
                    operation         = operation
                )
    
    return production_line_new

@login_required
def ajax_productionline_start_workflow(request):
    '''
    开始生产
    '''
    result = 0

    #create warehouse
    manu_item_group_id = int(request.POST.get('manu_item_group_id'))
    manu_item_group = ManufactureItemGroup.objects.get(id=manu_item_group_id)
    productionline = manu_item_group.productionline

    #create ManufactureItems, TODO: speed slow
    create_manufacture_items(manu_item_group)

    #set_workflow
    workflow = productionline.technology.workflow
    set_workflow(productionline,workflow)
    productionline.state = 2
    productionline.save()
    #set first_operation status
    operation_record = productionline.first_operation_record
    operation_record.status = 2
    operation_record.save()
    #set productionline.current_operation_record
    productionline.current_operation_record = operation_record
    productionline.save()

    data   = {'result':result,'msg':'error'}
    return HttpResponse('yuankong(' + json.dumps(data) + ');', content_type="application/json")

#create manufactureitems
def create_manufacture_items(manu_item_group):
    # technology_code = manu_item_group.productionline.technology.code
    # current_count = len(ManufactureItem.objects.filter(
    #     manu_item_group__productionline__technology_id=manu_item_group.productionline.technology.id
    # ))

    if manu_item_group.product and not manu_item_group.is_batch and not manu_item_group.manufacture_items.all():
        base_code = 'S-%s-' % manu_item_group.product.cad_code
        sim_items = ManufactureItem.objects.filter(
            code__startswith=base_code
            ).order_by('-id')
        if sim_items:
            num = int(sim_items[0].code.split('-')[-1]) + 1
        else:
            num = 1
        for i in range(manu_item_group.quantity):
            code = base_code + str(num+i)
            workflow = manu_item_group.productionline.technology.workflow
            productionline = create_new_productionline(manu_item_group.productionline.technology, manu_item_group)
            manufactureitem = ManufactureItem.objects.create(
                code            = code,
                manu_item_group = manu_item_group,
                batch_code      = manu_item_group.batch_code,
                productionline  = productionline,
                status          = 2
            )
            #set_workflow
            set_workflow(productionline,workflow)
            productionline.state = 2
            productionline.save()
            #set first_operation status
            operation_record = productionline.first_operation_record
            operation_record.status = 2
            operation_record.save()

            #set productionline current_operation_record
            # current_operation_records = OperationRecord.objects.filter(operation__state=workflow.initial_state)
            # if current_operation_records:
            productionline.current_operation_record = operation_record
            productionline.save()

    elif manu_item_group.is_batch:
        base_code = 'B-%s-' % manu_item_group.batch_code
        sim_items = ManufactureItem.objects.filter(
            code__startswith=base_code
            ).order_by('-id')
        if sim_items:
            num = int(sim_items[0].code.split('-')[-1]) + 1
        else:
            num = 1

        productionline = create_new_productionline(manu_item_group.productionline.technology, manu_item_group)
        manufactureitem = ManufactureItem.objects.create(
            code            = base_code + str(num),
            manu_item_group = manu_item_group,
            batch_code      = manu_item_group.batch_code,
            productionline  = productionline,
            status          = 2
        )
        #set_workflow
        workflow = manu_item_group.productionline.technology.workflow
        set_workflow(productionline,workflow)

        productionline.state = 2
        productionline.save()
        #set first_operation status
        operation_record = productionline.first_operation_record
        operation_record.status = 2
        operation_record.save()

        #set productionline current_operation_record
        # current_operation_records = OperationRecord.objects.filter(operation__state=workflow.initial_state)
        # if current_operation_records:
        productionline.current_operation_record = operation_record
        productionline.save()

@login_required
def productionline_states_list(request, productionline_id):
    redirecturl = request.REQUEST.get('next','')
    productionline = ProductionLine.objects.get(id=int(productionline_id))
    oper_group_records_list = []
    oper_group_records = productionline.oper_group_records.all()
    for count in range((oper_group_records.count()+4-1)/4):
        oper_group_records_list.append(oper_group_records[count*4:(count+1)*4])
    return render_to_response('productionline_states_list.html', {
        'productionline':productionline,'redirecturl':redirecturl,
        'oper_group_records_list':oper_group_records_list,
    }, context_instance=RequestContext(request))

@login_required
def productionline_send_programs_file(request,manufactureplan_id):
    redirecturl = request.REQUEST.get('next','')
    manufactureplan = ManufacturePlan.objects.get(id=manufactureplan_id)
    #create TransportList
    transport_list = TransportList.objects.create(
        list_category       = 6,
        transport_category  = 1,
        updated_by          = request.user,
        productionline      = manufactureplan.first_productionline
    )
    return HttpResponseRedirect(reverse(productionlines_list))


@login_required
def productionline_apply_materials(request,productionline_id):
    redirecturl = request.REQUEST.get('next','')
    productionline = ProductionLine.objects.get(id=int(productionline_id))
    #get manufactureplan
    manufactureplan = productionline.manufactureplan
    product = productionline.product
    #get parent_item
    parent_item = None
    item_type = ContentType.objects.get_for_model(product)
    parent_items = Item.objects.filter(content_type__pk=item_type.id,object_id=product.id).order_by('id')
    for item in parent_items:
        parent_item = item
        break
    #get items
    content_type = ContentType.objects.get(name='material',app_label='material',model='material')
    items = Item.objects.filter(content_type__pk=content_type.id).order_by('id')
    #get finish_time from manufactureplan.start_time
    finish_time = manufactureplan.start_time
    
    return render_to_response('productionline_apply_materials.html', {
        'productionline':productionline,'items':items,'manufactureplan':manufactureplan,
        'finish_time':str(finish_time),'redirecturl':redirecturl, 'l_m_manufacture_active':"active",
    }, context_instance=RequestContext(request))

@login_required
def ajax_create_bom_entries(request,productionline_id):
    result = 0
    productionline = ProductionLine.objects.get(id=int(productionline_id))
    #get parent_item
    product = productionline.product
    parent_item = None
    item_type = ContentType.objects.get_for_model(product)
    parent_items = Item.objects.filter(content_type__pk=item_type.id,object_id=product.id).order_by('id')
    if parent_items:
        parent_item = parent_items[0]
    
    finish_time = productionline.manufactureplan.start_time
    if request.method == 'POST':
        bom_entry_values = request.POST['bom_entry_values']
        #create bom_entries
        bom_entry_values_list = json.loads(bom_entry_values)
        for bom_entry_value in bom_entry_values_list:
            item = Item.objects.get(id=int(bom_entry_value['item_id']))
            qty = int(bom_entry_value['qty_val'])
            note = bom_entry_value['note_val']
            #create bom_entry
            bom_entry = BomEntry(
                parent = parent_item,
                item = item,
                qty = qty,
                updated_by = request.user,
                productionline = productionline,
                note = note,
                finish_time = finish_time,
            )
            bom_entry.save()
    data = {'result':result,'msg':msg[600+result],'state':state[600+result], 'l_m_manufacture_active':"active",}
    return HttpResponse('yuankong(' + json.dumps(data) + ');', content_type="application/json")

#replace by productionline_apply_devices
@login_required
def ajax_productionline_auto_apply_devices(request):
    import random
    result = 0
    productionline_id = int(request.POST['productionline_id'])
    productionline = ProductionLine.objects.get(id=productionline_id)
    for oper_group_record in productionline.oper_group_records.all():
        device = oper_group_record.operation_group.device
        content_type = ContentType.objects.get_for_model(device)
        device_entries = DeviceEntry.objects.filter(item__content_type_id=content_type.id,item__object_id=device.id)
        if device_entries:
            oper_group_record.device_items.add(random.choice(device_entries))

    data = {'result':result,'msg':'error',}
    return HttpResponse('yuankong(' + json.dumps(data) + ');', content_type="application/json")


@login_required
def productionline_apply_devices(request,productionline_id):
    redirecturl = request.REQUEST.get('next','')
    productionline = ProductionLine.objects.get(id=int(productionline_id))
    
    return render_to_response('productionline_apply_devices.html', {
        'productionline':productionline,'redirecturl':redirecturl, 'l_m_manufacture_active':"active",
    }, context_instance=RequestContext(request))

@login_required
def ajax_oper_group_record_get_can_applied_devices(request,oper_group_record_id):
    oper_group_record = OperationGroupRecord.objects.get(id=oper_group_record_id)
    data = "<select multiple class='form-control' style='height:160px'>"
    item0 = DeviceEntry.objects.get(id=0)
    if item0 in oper_group_record.device_items.all():
        data += "<option value='" + str(item0.id) + "' selected='selected'>无</option>"
    else:
        data += "<option value='" + str(item0.id) + "''>无</option>"
    for item in oper_group_record.can_applied_device_items:
        if item in oper_group_record.device_items.all():
            data += "<option value='" + str(item.id) + "' selected='selected'>" + item.__unicode__() + "</option>"
        else:
            data += "<option value='" + str(item.id) + "'>" + item.__unicode__() + "</option>"
    data += "</select>"
    data += "<p><small>按住Ctrl键可以选择多个</small></p>"
    return HttpResponse(data)

@login_required
def ajax_oper_group_record_set_applied_devices(request,oper_group_record_id):
    result = 0
    oper_group_record = OperationGroupRecord.objects.get(id=oper_group_record_id)
    oper_group_record.device_items.clear()
    device_entries = request.POST.get('device_entries',None)
    for device_entry_id in json.loads(device_entries):
        device_entry = DeviceEntry.objects.get(id=int(device_entry_id))
        oper_group_record.device_items.add(device_entry)

    data   = {'result':result,'msg':'msg'}
    return HttpResponse('yuankong(' + json.dumps(data) + ');', content_type="application/json")


@login_required
def ajax_productionline_apply_devices(request,productionline_id):
    result = 0
    productionline = ProductionLine.objects.get(id=int(productionline_id))
    if request.method == 'POST' and request.POST.get('attributes', False):
        attributes_list = json.loads(request.POST.get('attributes', False))
        for attribute_detail in attributes_list:
            oper_group_record = OperationGroupRecord.objects.get(id=int(attribute_detail['id']))
            device_entry = DeviceEntry.objects.get(id=int(attribute_detail['value']))
            if device_entry not in oper_group_record.device_items.all():
                oper_group_record.device_items.add(device_entry)
    
    data   = {'result':result,'msg':'error'}
    return HttpResponse('yuankong(' + json.dumps(data) + ');', content_type="application/json")

@login_required
def productionline_view_devices(request,productionline_id):
    redirecturl = request.REQUEST.get('next','')
    productionline = ProductionLine.objects.get(id=int(productionline_id))
    
    return render_to_response('productionline_view_devices.html', {
        'productionline':productionline,
        'redirecturl':redirecturl, 
        'l_m_manufacture_active':"active",
    }, context_instance=RequestContext(request))

'''
# this fauction will create transport_list from warehouse
def ajax_productionline_apply_devices(request,productionline_id):
    result = 0
    productionline = ProductionLine.objects.get(id=int(productionline_id))
    if request.method == 'POST':
        if request.POST.get('attributes', False):
            attributes_list = json.loads(request.POST.get('attributes', False))
            #create Transport
            transport_list = TransportList(
                list_category = 2,
                transport_category = 1,
                updated_by = request.user,
                productionline = productionline
            )
            transport_list.save()
            for attribute_detail in attributes_list:
                oper_group_record = OperationGroupRecord.objects.get(id=int(attribute_detail['id']))
                device_entry = DeviceEntry.objects.get(id=int(attribute_detail['value']))
                
                #create TransportListDetail
                transport_detail = TransportListDetail(
                    transport_list = transport_list,
                    item_entry_code = device_entry.internal_code,
                    item = device_entry.item,
                    unit = '个',
                    updated_by = request.user,
                    content_object = oper_group_record
                )
                transport_detail.save()
        
    data   = {'result':result,'msg':'error'}
    return HttpResponse('yuankong(' + json.dumps(data) + ');', content_type="application/json")

def productionline_apply_knifes(request,productionline_id):
    redirecturl = request.REQUEST.get('next','')
    productionline = ProductionLine.objects.get(id=int(productionline_id))
    knife_items = []
    for item in DeviceEntry.objects.all():
        if item.item.is_knife and item.location_id==1 and item.qty>0:
            knife_items.append(item)
    
    return render_to_response('productionline_apply_knifes.html', {
        'productionline':productionline,'knife_items':knife_items,'redirecturl':redirecturl
    }, context_instance=RequestContext(request))

def productionline_apply_tools(request,productionline_id):
    redirecturl = request.REQUEST.get('next','')
    productionline = ProductionLine.objects.get(id=int(productionline_id))
    tool_items = []
    for item in DeviceEntry.objects.all():
        if item.item.is_tool:
            tool_items.append(item)
    
    return render_to_response('productionline_apply_knifes.html', {
        'productionline':productionline,'tool_items':tool_items,'redirecturl':redirecturl
    }, context_instance=RequestContext(request))

def ajax_productionline_apply_knifes(request,productionline_id):
    result = 0
    productionline = ProductionLine.objects.get(id=int(productionline_id))
    if request.method == 'POST' and request.POST.get('attributes', False):
        attributes_list = json.loads(request.POST.get('attributes', False))
        #create Transport
        transport_list = TransportList(
            list_category = 3,
            transport_category = 1,
            updated_by = request.user,
            productionline = productionline
        )
        transport_list.save()
        for attribute_detail in attributes_list:
            operation_record = OperationRecord.objects.get(id=int(attribute_detail['operation_record_id']))
            knife_item = DeviceEntry.objects.get(id=int(attribute_detail['knife_item_id']))
            
            #create TransportListDetail
            transport_detail = TransportListDetail(
                transport_list = transport_list,
                item_entry_code = knife_item.internal_code,
                item = knife_item.item,
                unit = '个',
                updated_by = request.user,
                content_object = operation_record
            )
            transport_detail.save()
    
    data   = {'result':result,'msg':'error'}
    return HttpResponse('yuankong(' + json.dumps(data) + ');', content_type="application/json")

def ajax_productionline_apply_tools(request,productionline_id):
    result = 0
    productionline = ProductionLine.objects.get(id=int(productionline_id))
    device_items = []
    if request.method == 'POST':
        if request.POST.get('attributes', False):
            attributes_list = json.loads(request.POST.get('attributes', False))
            for attribute_detail in attributes_list:
                oper_group_record = OperationGroupRecord.objects.get(id=int(attribute_detail['id']))
                device_item = DeviceEntry.objects.get(id=int(attribute_detail['value']))
                oper_group_record.device_items.add(device_item)
                oper_group_record.save()
                device_items.append(device_item)
    
    #create Transport
    transport_list = TransportList(
        list_category = 2,
        transport_category = 1,
        updated_by = request.user,
        productionline = productionline
    )
    transport_list.save()
    for device_item in device_items:
        transport_detail = TransportListDetail(
            transport_list = transport_list,
            item_entry_code = device_item.internal_code,
            item = device_item.item,
            unit = '个',
            updated_by = request.user,
        )
        transport_detail.save()
    data   = {'result':result,'msg':'error'}
    return HttpResponse('yuankong(' + json.dumps(data) + ');', content_type="application/json")
'''



@login_required
def ajax_get_qa_record_attributes_modal_content(request):
    result = 0
    html_title = ''
    html_content = ''
    
    if request.method == 'POST':
        qa_record_id = int(request.POST['qa_record_id'])
        qa_record = QARecord.objects.get(id=qa_record_id)
        html_title += "%s" % qa_record
        for qa_record_attribute in qa_record.qa_record_attributes.all():
            html_content = html_content + '<tr>' + '<td>'
            html_content = html_content + qa_record_attribute.attribute.name
            html_content = html_content + '(' + qa_record_attribute.attribute.unit + ')'
            html_content = html_content + '</td>' + '<td>'
            if qa_record_attribute.product_attribute:
                html_content = html_content + str(qa_record_attribute.product_attribute.absolute_value)
                html_content = html_content + '(' + str(qa_record_attribute.product_attribute.upper_deviation)
                html_content = html_content + ', ' + str(qa_record_attribute.product_attribute.lower_deviation) + ')'
            html_content = html_content + '</td>'
            if qa_record_attribute.excessive:
                html_content = html_content + "<td bgcolor='#FFFF00'>"
            else:
                html_content = html_content + "<td>"
            
            html_content = html_content + str(qa_record_attribute.absolute_value)
            html_content = html_content + "</td>" + "</tr>"
    
    data = {'result':result,'msg':'error','title':html_title,'content':html_content,}
    return HttpResponse('yuankong(' + json.dumps(data) + ');', content_type="application/json")

@login_required
def operation_working_device_items_list(request):
    device_items = DeviceEntry.objects.filter(internal_code__icontains="KCSK").order_by("id")

    is_contains_batch_check = getattr(settings,'IS_USE_BATCH_CHECK',False)

    return render_to_response('operation_working_device_items_list.html', {
        'device_items':device_items, 'l_m_manufacture_active':"active",
        'is_contains_batch_check':is_contains_batch_check,
    }, context_instance=RequestContext(request))

########################################
#how to find current_manufacture_items by device_item
#device_item -> productionlines
#    productionline -> current_state -> current_operation_record
#    productionline.oper_group_records
#        oper_group_record.device == device
#            oper_group_record.operation_records
#                operation_record == current_operation_record
########################################
@login_required
def operation_working_start(request, device_item_id):
    # 1. device_item_id) == 0 移到其它中了
    device_entry = DeviceEntry.objects.get(id=device_item_id)
    productionline_id_list = list(set([ogr.productionline.id for ogr in device_entry.oper_group_record.all()]))
    #current_productionlines = [p for p in productionlines if not (p.state == 3 and p.can_export)]

    productionlines = ProductionLine.objects.filter(id__in=productionline_id_list)

    # 排除其它中显示的内容
    mis_id_list = get_mis_id_list_other()

    use_new_qa_modal = getattr(settings,'USE_NEW_QA_MODAL',False)

    current_productionlines = []
    for productionline in productionlines:
        if productionline.is_show_in_operating_platform:
            current_manufacture_items = []
            for manufacture_item in productionline.self_manufacture_items:
                if (manufacture_item.id not in mis_id_list) and device_entry in manufacture_item.current_operation_record.oper_group_record.device_items.all() or productionline.manu_item_group.is_batch:
                    current_manufacture_items.append(manufacture_item)
            if current_manufacture_items:
                one_node = {'productionline':productionline, 'manufacture_items':current_manufacture_items}
                current_productionlines.append(one_node)

    # #select the device
    # #device_item = DeviceItem.objects.get(id=device_item_id)
    # employee = Employee.objects.get(user_id=request.user.id)
    # device_entry_item = DeviceEntry.objects.get(id=device_item_id)
    
    # current_productionlines = []
    # current_operation_record = None
    # operation_group_records = device_entry_item.oper_group_record.all()

    # new_operation_group_records = []
    # device_items = []
    # for operation_group_record in operation_group_records:
    #     oper_group_records = operation_group_record.productionline.oper_group_records.all()
    #     for oper_group_record in oper_group_records:
    #         device_items.extend(oper_group_record.device_items.all())
    # for device_item in device_items:
    #     new_operation_group_records.extend(device_item.oper_group_record.all())
    # operation_group_records = new_operation_group_records

    # for operation_group_record in operation_group_records:
    #     if operation_group_record.productionline.manu_item_groups.all() and operation_group_record.productionline not in current_productionlines:
    #         current_operation_record = operation_group_record.productionline.current_operation_record
    #         if current_operation_record and current_operation_record.oper_group_record == operation_group_record and current_operation_record.status in [2,3,4,5,6,7,8]:
    #             current_productionlines.append(operation_group_record.productionline)
    #         if operation_group_record.productionline.manu_item_group.is_batch and operation_group_record.productionline not in current_productionlines:
    #             current_productionlines.append(operation_group_record.productionline)
    #     # #excessive qa_record
    #     # elif current_operation_record and current_operation_record.status in [6,7]:
    #     #     for manu_item_group in current_operation_record.oper_group_record.productionline.manu_item_groups.all():
    #     #         if not manu_item_group.current_manufacture_items_passed:
    #     #             current_productionlines.append(operation_group_record.productionline)

    return render_to_response('operation_working_start.html', {
        'use_new_qa_modal':use_new_qa_modal,
        'device_item':device_entry,'current_productionlines':current_productionlines, 'l_m_manufacture_active':"active",
    }, context_instance=RequestContext(request))

@login_required
def operation_working_timing(request,device_entry_id,manufacture_item_id):
    redirecturl = request.REQUEST.get('next','')

    # check object exists ?
    device_entry = get_object_or_none(DeviceEntry,id=device_entry_id)
    employee = get_object_or_none(Employee,user_id=request.user.id)
    if device_entry is None:
        messages.info(request,_("device entry does not exists,please contact admin add it"))
        return HttpResponseRedirect(reverse('operation_working_start',args=[device_entry_id]))
    if employee is None:
        messages.info(request,_("employee does not exists,please contact admin add it"))
        return HttpResponseRedirect(reverse('operation_working_start',args=[device_entry_id]))


    # 是否启用新的流程
    use_new_check_flow = getattr(settings,'USE_NEW_CHECK_FLOW',False)
    mis_id_list = get_all_check_manu_items()

    has_relation = 0
    manufacture_relation = None
    # 工件
    manufacture_item = ManufactureItem.objects.get(id=manufacture_item_id)
    # 当前工步
    current_operation_record = manufacture_item.current_operation_record
    #find product attributes
    #product = current_operation_record.operation.product
    # 工步属性
    product_attributes = OperationAttribute.objects.filter(operation=current_operation_record.operation)
    # logger.info(product_attributes)

    # 确认交接记录是否需要填写
    if manufacture_item.self_records.filter(qa_excessive_status=2).filter(Q(type=1)|Q(type=2)).exists():
        is_relation_note_required = True
    else:
        is_relation_note_required = False

    # 是否是检验
    if manufacture_item.id in mis_id_list:
        is_qa_inspector = True
    else:
        is_qa_inspector = False

    #find manufacture_relation
    # 生产记录
    manufacture_records = ManufactureRecord.objects.filter(manufacture_item=manufacture_item,operation_record=current_operation_record).order_by('-date_added')
    if len(manufacture_records) > 0:
        #find manufacture_relation 查找交接记录
        manufacture_relations = ManufactureRelation.objects.filter(from_manufacture_record=manufacture_records[0]).order_by('-date_modified')
        if len(manufacture_relations) > 0:
            if manufacture_relations and manufacture_relations[0].status == 1:
                manufacture_relation = manufacture_relations[0]
                has_relation = 1
        elif not manufacture_relations and len(manufacture_records) > 1:
            manufacture_relations = ManufactureRelation.objects.filter(from_manufacture_record=manufacture_records[1]).order_by('-date_modified')
            if manufacture_relations and manufacture_relations[0].status == 3:
                manufacture_relation = manufacture_relations[0]
                has_relation = 3
    #if DoubleRecord
    self_record_attributes = []
    if current_operation_record.status == 4:
        self_records = QARecord.objects.filter(operation_record=current_operation_record,type=1).order_by('-updated_at')
        if len(self_records) > 0:
            self_record_attributes = QARecordAttribute.objects.filter(qa_record=self_records[0])

    #if InspectorRecord
    double_record_attributes = []
    if current_operation_record.status == 5:
        double_records = QARecord.objects.filter(operation_record=current_operation_record,type=2).order_by('-updated_at')
        if len(double_records) > 0:
            double_record_attributes = QARecordAttribute.objects.filter(qa_record=double_records[0])

    if manufacture_item.is_batch:
        can_finish_tag = True if device_entry in manufacture_item.current_operation_record.oper_group_record.device_items.all() else False
        return render_to_response('operation_working_timing_batch.html', {
            'has_relation':has_relation,'manufacture_relation':manufacture_relation,
            'manufacture_item':manufacture_item,'product_attributes':product_attributes,
            'redirecturl':redirecturl,'employee':employee,'device_entry':device_entry,
            'can_finish_tag':can_finish_tag,
            'l_m_manufacture_active':"active",
            'is_qa_inspector':is_qa_inspector,
            "is_relation_note_required":is_relation_note_required,
        }, context_instance=RequestContext(request))
    else:
        return render_to_response('operation_working_timing.html', {
            'has_relation':has_relation,'manufacture_relation':manufacture_relation,
            'manufacture_item':manufacture_item,'product_attributes':product_attributes,
            'redirecturl':redirecturl,'employee':employee,'device_entry':device_entry,
            'l_m_manufacture_active':"active",
            'is_qa_inspector':is_qa_inspector,
            "is_relation_note_required":is_relation_note_required,
            'use_new_check_flow':use_new_check_flow,
        }, context_instance=RequestContext(request))











########################################
#ajax
########################################



msg = {
    0:'success',
    1:'result default value',
    2:'warning',
    #operation_record
    101:'find operation_record error',
    102:'create operation_record error',
    103:'edit operation_record error',
    #manufacture_record
    201:'find manufacture_record error',
    202:'create manufacture_record error',
    203:'edit manufacture_record error',
    #manufacture_relation
    301:'find manufacture_relation error',
    302:'create manufacture_relation error',
    303:'edit manufacture_relation error',
    #qa_record
    401:'find qa_record error',
    402:'create qa_record error',
    403:'edit qa_record error',
    #timesheet
    501:'find timesheet error',
    502:'create timesheet error',
    503:'edit timesheet error',
    #bom_entry
    600:'create bom_entry ok',
    603:'create bom_entry error',
    #bom_entry
    700:'create bom_entry ok',
    702:'create bom_entry error',
    703:'can create bom_entry',
}
state = {
    0:'success',
    1:'ERROR',
    #work
    100:'start work ok',
    101:'you can not start the work',
    102:'you are already start work, do not repeat submit',
    103:'end work ok',
    104:'you can not end the work',
    #rest
    200:'start rest ok',
    201:'you can not start the rest',
    202:'you are already start rest, do not repeat submit',
    203:'end rest ok',
    204:'you can not end the rest',
    #relation
    300:'create relation ok',
    301:'you can not create the relation, you have not do anything',
    302:'you are already create relation, do not repeat submit',
    303:'end relation ok',
    304:'you can not end the relation',
    #qa
    400:'start qa ok',
    401:'you can not start the qa',
    402:'you are already start qa, do not repeat submit',
    403:'end qa ok',
    404:'you can not end the qa',
    #bom_entry
    600:'create bom_entry ok',
    603:'create bom_entry error',
}

########################################
#create or find manufacture_record
#create work timesheet
########################################
@login_required
def item_working_work(request):
    result = 1

    now = datetime.datetime.now()
    employee = Employee.objects.get(user_id=request.user.id)
    
    if request.method == 'POST':
        manufacture_item_code = request.POST['item_code']
        status = request.POST['status']
        device_entry_id = int(request.POST['device_entry_id'])
        device_entry = DeviceEntry.objects.get(id=device_entry_id)
        manufacture_item = ManufactureItem.objects.get(code=manufacture_item_code)
        current_operation_record = manufacture_item.current_operation_record
        #create or find manufacture_record
        manufacture_record = None
        manufacture_records = ManufactureRecord.objects.filter(
            manufacture_item=manufacture_item,
            operation_record=current_operation_record,
            device_entry=device_entry
        ).order_by('-id')
        if manufacture_records:
            manufacture_record = manufacture_records[0]
        else:
            result, manufacture_record = create_manufacture_record(employee,manufacture_item,current_operation_record,device_entry)
        #create timesheet
        result, timesheet = create_timesheet(employee,manufacture_record)

    data = {'result':result,'msg':msg[result],'state':state[100+result],'date':str(timesheet.start)}
    return HttpResponse('yuankong(' + json.dumps(data) + ');', content_type="application/json")





########################################
#find manufacture_record
#end timesheet
########################################
@login_required
def item_working_rest(request):
    result = 0

    date = ''
    employee = Employee.objects.get(user=request.user)
    if request.method == 'POST':
        manufacture_item_code = request.POST['item_code']
        manufacture_item = ManufactureItem.objects.get(code=manufacture_item_code)
        device_entry_id = int(request.POST['device_entry_id'])
        device_entry = DeviceEntry.objects.get(id=device_entry_id)
        current_operation_record = manufacture_item.current_operation_record
        
        #find manufacture_record
        manufacture_records = ManufactureRecord.objects.filter(
            manufacture_item=manufacture_item,
            operation_record=current_operation_record,
            device_entry=device_entry
            ).order_by('-date_added')
        if len(manufacture_records) > 0:
            #end timesheet
            result, timesheet = end_timesheet(employee,manufacture_records[0])
            if timesheet:
                date = str(timesheet.end)
        else:
            result = 1

    data   = {'result':result,'msg':msg[result],'state':state[200+result],'date':date}
    return HttpResponse('yuankong(' + json.dumps(data) + ');', content_type="application/json")



########################################
#find manufacture_record
#create cmanufacture_relation
#end timesheet
########################################
@login_required
def item_working_relation_start(request):
    result = 0
    
    employee = Employee.objects.get(user=request.user)
    if request.method == 'POST':
        manufacture_item_code = request.POST['item_code']
        note = request.POST['note']
        device_entry_id = int(request.POST['device_entry_id'])
        device_entry = DeviceEntry.objects.get(id=device_entry_id)
        manufacture_item = ManufactureItem.objects.get(code=manufacture_item_code)
        current_operation_record = manufacture_item.current_operation_record
        #find manufacture_record
        manufacture_records = ManufactureRecord.objects.filter(
            manufacture_item=manufacture_item,
            operation_record=current_operation_record,
            device_entry=device_entry
            ).order_by('-date_added')
        logger.info(manufacture_records)
        if len(manufacture_records) > 0:
            #create manufacture_relation
            result, manufacture_relation = create_manufacture_relation(manufacture_records[0],employee,note)
            #end timesheet
            end_timesheet(employee,manufacture_records[0])
        else:
            result = 1
            
    logger.info(result)
    data   = {'result':result,'msg':msg[result],'state':state[300+result],}
    return HttpResponse('yuankong(' + json.dumps(data) + ');', content_type="application/json")



########################################
#
########################################
@login_required
def item_working_relation_handle(request):
    result = 0

    employee = Employee.objects.get(user=request.user)
    if request.method == 'POST':
        manufacture_item_code = request.POST['item_code']
        manufacture_item = ManufactureItem.objects.get(code=manufacture_item_code)
        device_entry_id = int(request.POST['device_entry_id'])
        device_entry = DeviceEntry.objects.get(id=device_entry_id)
        current_operation_record = manufacture_item.current_operation_record
        result, manufacture_record = create_manufacture_record(employee,manufacture_item,current_operation_record,device_entry)

        status = int(request.POST['status'])
        manufacture_relation_id = request.POST['relation_id']
        manufacture_relation = ManufactureRelation.objects.get(id=manufacture_relation_id)
        manufacture_relation.to_manufacture_record = manufacture_record
        manufacture_relation.to_employee = employee
        manufacture_relation.status = status
        manufacture_relation.save()
    data = {'result':result,'msg':msg[result],'state':state[result],}
    return HttpResponse('yuankong(' + json.dumps(data) + ');', content_type="application/json")


'''
########################################
#not use
########################################
@login_required
def item_working_relation_reject(request):
    result = 0
    if request.method == 'POST':
        manufacture_relation_id = request.POST['relation_id']
        manufacture_relation = ManufactureRelation.objects.get(id=manufacture_relation_id)
        manufacture_relation.status = 3
        manufacture_relation.save()
    data   = {'result':result,'msg':msg[result],'state':state[result],}
    return HttpResponse('yuankong(' + json.dumps(data) + ');', content_type="application/json")
'''


########################################
#create manufacture_record
#modify manufacture_record.status
#end timesheet
########################################
@login_required
def item_working_finish(request):
    result = 0
    user = User.objects.get(id=1)
    employee = Employee.objects.get(user=user)
    if request.method == 'POST':
        manufacture_item_code = request.POST['item_code']
        manufacture_item = ManufactureItem.objects.get(code=manufacture_item_code)
        device_entry_id = int(request.POST['device_entry_id'])
        device_entry = DeviceEntry.objects.get(id=device_entry_id)
        current_operation_record = manufacture_item.current_operation_record

        # 对填写的数据进行校验，填写的属性值必须是浮点数
        attributes = request.POST.get('attributes') if request.POST.get('attributes') else None
        attributes_list = json.loads(attributes) if attributes else []
        for d in attributes_list:
            v = d.get('value')
            if v is None:
                result = 1
                _msg = ugettext('value must be required')
                data   = {'result':result,'msg':msg[result],'state':_msg,}
                return HttpResponse('yuankong(' + json.dumps(data) + ');', content_type="application/json")
            try:
                float(v)
            except Exception:
                result = 1
                _msg = ugettext('value must be a decimal number')
                data   = {'result':result,'msg':msg[result],'state':_msg,}
                return HttpResponse('yuankong(' + json.dumps(data) + ');', content_type="application/json")
        # 校验结束
        if int(request.POST['type']) == 6:
            manufacture_item.status = 6
            manufacture_item.save()
        #create qa_record
        if attributes:
            result = create_qa_record(employee,current_operation_record,manufacture_item,attributes_list,int(request.POST['type']))
        #find manufacture_record
        manufacture_records = ManufactureRecord.objects.filter(
            manufacture_item = manufacture_item,
            operation_record = current_operation_record,
            device_entry     = device_entry
        ).order_by('-date_added')
        if len(manufacture_records) > 0:
            #end timesheet
            end_timesheet(employee,manufacture_records[0])

        #do_transition
        if manufacture_item.status == 6:
            result = productionline_do_transition(request.user,manufacture_item.productionline,6)


    data   = {'result':result,'msg':msg[result],'state':state[result],}
    return HttpResponse('yuankong(' + json.dumps(data) + ');', content_type="application/json")




########################################
#utils
########################################

# productionline_do_transition 移到了 utils 中了

@login_required
def ajax_import_manufacture_items(request):
    # import pdb; pdb.set_trace()
    result = 0
    productionline_id = int(request.POST['productionline_id'])
    productionline = ProductionLine.objects.get(id=productionline_id)
    location = Location.objects.get(id=1)
    #create TransportList
    transport_list = TransportList.objects.create(
        list_category = 1,
        transport_category = 2,
        updated_by = request.user,
        applicat = request.user,
        productionline = productionline
    )
    productionline.location_status = 2
    productionline.save()
    for manufacture_item in productionline.no_excessive_manufacture_items:
        #create item
        product = manufacture_item.manu_item_group.product
        content_type = ContentType.objects.get_for_model(product)
        items = Item.objects.filter(content_type_id=content_type.id,object_id=product.id)
        if items:
            item = items[0]
        else:
            item = Item.objects.create(
                code            = manufacture_item.code,
                content_type_id = content_type.id,
                object_id       = product.id
            )

        #create TransportListDetail
        transport_detail = TransportListDetail.objects.create(
            transport_list  = transport_list,
            item_entry_code = manufacture_item.code,
            item            = item,
            qty             = manufacture_item.qty,
            unit            = '个',
            updated_by      = request.user,
            content_object  = manufacture_item,
            location        = location,
        )

    data   = {'result':result,'msg':'error'}
    return HttpResponse('yuankong(' + json.dumps(data) + ');', content_type="application/json")

@login_required
def ajax_export_manufacture_items(request):
    result = 0
    productionline_id = int(request.POST['productionline_id'])
    productionline = ProductionLine.objects.get(id=productionline_id)
    location = Location.objects.get(id=1)
    #get TransportList
    transport_lists_in = productionline.transport_lists.filter(list_category=1,transport_category=2).order_by('-created_at')
    #create TransportList
    transport_list_out = TransportList.objects.create(
        list_category = 1,
        transport_category = 1,
        updated_by = request.user,
        applicat = request.user,
        productionline = productionline
    )
    productionline.location_status = 4
    productionline.save()
    for transport_detail in transport_lists_in[0].transport_list_details.all():
        #create TransportListDetail
        transport_detail_new = TransportListDetail.objects.create(
            transport_list  = transport_list_out,
            item_entry_code = transport_detail.item_entry_code,
            item            = transport_detail.item,
            qty             = transport_detail.qty,
            unit            = transport_detail.unit,
            updated_by      = request.user,
            content_object  = transport_detail.content_object,
            location        = location,
        )

    data   = {'result':result,'msg':'error'}
    return HttpResponse('yuankong(' + json.dumps(data) + ');', content_type="application/json")

def create_timesheet(employee,manufacture_record):
    result = 0
    now = datetime.datetime.now()
    manufacture_record_type = ContentType.objects.get_for_model(manufacture_record)
    timesheets = Timesheet.objects.filter(person=employee,content_type__pk=manufacture_record_type.id,object_id=manufacture_record.id,date=now.date()).order_by('-start')
    if len(timesheets) > 0 and timesheets[0].start==timesheets[0].end:
        timesheet = timesheets[0]
        result = 2
    else:
        timesheet = Timesheet(
            person = employee,
            start  = now,
            date   = now.date(),
            end    = now,
            content_object = manufacture_record,
        )
        timesheet.save()

    return result, timesheet

def end_timesheet(employee,manufacture_record):
    result = 0

    now = datetime.datetime.now()
    timesheet = None
    manufacture_record_type = ContentType.objects.get_for_model(manufacture_record)
    timesheets = Timesheet.objects.filter(person=employee,content_type__pk=manufacture_record_type.id,object_id=manufacture_record.id,date=now.date()).order_by('-start')
    if len(timesheets) > 0:
        if timesheets[0].start == timesheets[0].end:
            timesheets[0].end = now
            timesheets[0].save()
        else:
            result = 2
        timesheet = timesheets[0]
    return result, timesheet

def create_manufacture_record(employee,manufacture_item,current_operation_record,device_entry):
    result = 0
    #create manufacture_record
    manufacture_record = ManufactureRecord(
        manufacture_item  = manufacture_item,
        operation_record  = current_operation_record,
        device_entry      = device_entry,
        status            = current_operation_record.status,
    )
    manufacture_record.save()

    current_operation_record.status = 2
    current_operation_record.save()
    return result, manufacture_record

def create_manufacture_relation(from_manufacture_record,from_employee,note):
    result = 0
    now = datetime.datetime.now()
    manufacture_relations = ManufactureRelation.objects.filter(from_manufacture_record=from_manufacture_record,from_employee=from_employee,date=now.date()).order_by('-date_modified')
    if len(manufacture_relations) > 0 and manufacture_relations[0].status == 1:
        manufacture_relation = manufacture_relations[0]
        result = 3
    else:
        manufacture_relation = ManufactureRelation(
            from_manufacture_record = from_manufacture_record,
            from_employee = from_employee,
            note = note,
            date = now.date(),
        )
        manufacture_relation.save()
    return result, manufacture_relation

def create_qa_record(employee,current_operation_record,manufacture_item,attributes_list,qa_type):
    result = 0
    #create qa_record
    qa_record = QARecord(
        employee         = employee,
        operation_record = current_operation_record,
        manufacture_item = manufacture_item,
        type             = int(qa_type),
    )
    qa_record.save()

    #add attributes to this qa_record
    # attributes_list = json.loads(attributes)
    for attribute_detail in attributes_list:
        attribute_id = attribute_detail['id'].replace('qa_fill','')
        attribute = Attribute.objects.get(id=int(attribute_id))
        #create qa_record_attribute
        attribute_value = attribute_detail.get('value',0.0)
        qa_record_attribute = QARecordAttribute(
            qa_record = qa_record,
            attribute = attribute,
            absolute_value = float(attribute_value),
        )

        #set qa_excessive_status
        difference = qa_record_attribute.absolute_value - float(qa_record_attribute.product_attribute.absolute_value)
        upper_deviation = float(qa_record_attribute.product_attribute.upper_deviation)
        lower_deviation = float(qa_record_attribute.product_attribute.lower_deviation)
        if (not (abs(difference - upper_deviation) < 0.00001)) or (not (abs(lower_deviation - difference) < 0.00001)):
            qa_record_attribute.qa_excessive_status = 2
            if not qa_record.is_qa_excessive_status_excessive:
                qa_record.qa_excessive_status = 2
                qa_record.save()
            if current_operation_record.qa_excessive_status in [1,3]:
                current_operation_record.qa_excessive_status = 2
                current_operation_record.save()
        qa_record_attribute.save()

    if qa_record.qa_excessive_status == 2:
        #generate code
        now = datetime.datetime.now()
        count = RejectProductRecord.objects.filter(date_added__startswith=now.date()).count()
        #create reject_product_record
        reject_product_record = RejectProductRecord(
            productionline    = qa_record.operation_record.oper_group_record.productionline,
            code              = '%s%03d' %(now.strftime('%Y%m%d'),count+1),
            qa_record         = qa_record,
            quality_problems  = '',
            reason_analysis   = '',
            processing_result = '',
        )
        reject_product_record.save()

    # manufacture_item.status = 3 + type
    # manufacture_item.save()
    # current_operation_record.status = 3 + type
    # current_operation_record.save()
    
    #status = current_operation_record.QA_status

    return result

@login_required
def productionlines_monitoring(request):
    from manufactureplan.models import CHOICE_STATE_STATUS, color_name
    #CHOICE_STATE_STATUS = [list(STATUS).appent(color_name[STATUS[0]]) for list(STATUS) in CHOICE_STATE_STATUS]
    new_CHOICE_STATE_STATUS = []
    for STATUS in CHOICE_STATE_STATUS:
        STATUS_list = list(STATUS)
        STATUS_list.append(color_name[STATUS[0]])
        STATUS = tuple(STATUS_list)
        new_CHOICE_STATE_STATUS.append(STATUS)

    manu_item_groups = [m for m in ManufactureItemGroup.objects.all() if m.productionline and get_workflow(m.productionline)]
    return render_to_response('productionlines_monitoring.html', {
        'manu_item_groups':manu_item_groups,'CHOICE_STATE_STATUS':tuple(new_CHOICE_STATE_STATUS),
        'l_m_manufacture_active':"active",
    }, context_instance=RequestContext(request))



#xadmin BaseActionView
from xadmin.plugins.actions import BaseActionView

class BatchStartWorkflowAction(BaseActionView):
    action_name = "start_workflow"
    description = _(u'Batch start workflow %(verbose_name_plural)s')
    model_perm = 'change'

    def do_action(self, queryset):
        for productionline in queryset:
            '''
            bom_entries = BomEntry.objects.filter(productionline = productionline)
            if not bom_entries:
                return 0
            '''
            if not productionline.item_entries_ok:#materials ok
                return 0
            else:
                workflow = productionline.technology.workflow
                set_workflow(productionline,workflow)
                productionline.state = 2
                productionline.save()
                #productionline.first_operation.status = 2
                #productionline.first_operation.save()
                for manufacture_item in productionline.self_manufacture_items:
                    manufacture_item.status = 2
                    manufacture_item.save()



@login_required
def operation_working_check(request):
    '''
    单独的工作台 : 检验
    当当前工步为检验时,在这个工作台下显示,并能进行操作
    '''
    # mis_id_list = ManufactureItem.objects.filter(productionline__current_operation_record__operation__attributes__isnull=False).values_list('id',flat=True)

    mis_id_list = get_all_check_manu_items()

    productionline_id_list = get_batch_productionlines(batch_type="check")
    production_lines = ProductionLine.objects.filter(id__in=productionline_id_list)
    current_productionlines = []
    for pl in production_lines:
        if pl.is_show_in_operating_platform:
            current_manufacture_items = []
            for manufacture_item in pl.self_manufacture_items:
                # 只显示当前状态 为检验 的工件
                if manufacture_item.id in mis_id_list:
                    current_manufacture_items.append(manufacture_item)
            # 有数据才显示
            if current_manufacture_items:
                one_node = {
                    'productionline':pl,
                    'manufacture_items':current_manufacture_items,
                }
                current_productionlines.append(one_node)
    page_title = _("check")

    # 是否允许批量操作，只有在 productionline 允许，下面变量为真的时候才显示批量操作
    is_batch_handle_allowed = True
    use_new_qa_modal = getattr(settings,'USE_NEW_QA_MODAL',False)
    
    return render(request,'operation_working_start.html',{
        'use_new_qa_modal':use_new_qa_modal,
        'l_m_manufacture_active':"active",
        'page_title':page_title,
        'source':"check",
        "is_batch_check":True,
        "is_batch_handle_allowed":is_batch_handle_allowed,
        'current_productionlines':current_productionlines,
    })

@login_required
def operation_working_wipe_burr(request):
    '''
    单独的工作台 : 去毛刺
    '''
    mis_id_list = get_all_wipe_burr_manu_items()

    # 第二步,找到 对应的 productionline
    productionline_id_list = get_batch_productionlines(batch_type="wipe_burr")

    production_lines = ProductionLine.objects.filter(id__in=productionline_id_list)
    current_productionlines = []
    for pl in production_lines:
        if pl.is_show_in_operating_platform:
            current_manufacture_items = []
            for manufacture_item in pl.self_manufacture_items:
                # 只显示当前状态 为去毛刺 的工件
                if manufacture_item.id in mis_id_list:
                    current_manufacture_items.append(manufacture_item)
            # 有数据才显示
            if current_manufacture_items:
                one_node = {
                    'productionline':pl,
                    'manufacture_items':current_manufacture_items,
                }
                current_productionlines.append(one_node)
    page_title = _("wipe burr")

    # 是否允许批量操作，只有在 productionline 允许，下面变量为真的时候才显示批量操作
    is_batch_handle_allowed = True
    use_new_qa_modal = getattr(settings,'USE_NEW_QA_MODAL',False)

    return render(request,'operation_working_start.html',{
        'use_new_qa_modal':use_new_qa_modal,
        'l_m_manufacture_active':"active",
        'page_title':page_title,
        'source':"wipe_burr",
        "is_batch_handle_allowed":is_batch_handle_allowed,
        'current_productionlines':current_productionlines,
    })

@login_required
def operation_working_heattreatment(request):
    '''
    单独的工作台 : 热处理
    '''
    mis_id_list = get_all_heattreatment_manu_items()

    # 第二步,找到 对应的 productionline
    productionline_id_list = get_batch_productionlines(batch_type="heattreatment")

    production_lines = ProductionLine.objects.filter(id__in=productionline_id_list)
    current_productionlines = []
    for pl in production_lines:
        if pl.is_show_in_operating_platform:
            current_manufacture_items = []
            for manufacture_item in pl.self_manufacture_items:
                # 只显示当前状态 为热处理 的工件
                if manufacture_item.id in mis_id_list:
                    current_manufacture_items.append(manufacture_item)
            # 有数据才显示
            if current_manufacture_items:
                one_node = {
                    'productionline':pl,
                    'manufacture_items':current_manufacture_items,
                }
                current_productionlines.append(one_node)
    page_title = _("heattreatment")

    # 是否允许批量操作，只有在 productionline 允许，下面变量为真的时候才显示批量操作
    is_batch_handle_allowed = True
    use_new_qa_modal = getattr(settings,'USE_NEW_QA_MODAL',False)

    return render(request,'operation_working_start.html',{
        'use_new_qa_modal':use_new_qa_modal,
        'l_m_manufacture_active':"active",
        'page_title':page_title,
        'source':"heattreatment",
        "is_batch_handle_allowed":is_batch_handle_allowed,
        'current_productionlines':current_productionlines,
    })

@login_required
def operation_working_incasement(request):
    '''
    单独的工作台: 装箱
    '''
    mis_id_list = get_all_incasement_manu_items()

    # 第二步,找到 对应的 productionline
    productionline_id_list = get_batch_productionlines(batch_type="incasement")

    production_lines = ProductionLine.objects.filter(id__in=productionline_id_list)
    current_productionlines = []
    for pl in production_lines:
        if pl.is_show_in_operating_platform:
            current_manufacture_items = []
            for manufacture_item in pl.self_manufacture_items:
                if manufacture_item.id in mis_id_list:
                    current_manufacture_items.append(manufacture_item)
            # 有数据才显示
            if current_manufacture_items:
                one_node = {
                    'productionline':pl,
                    'manufacture_items':current_manufacture_items,
                }
                current_productionlines.append(one_node)
    page_title = _("incasement")

    # 是否允许批量操作，只有在 productionline 允许，下面变量为真的时候才显示批量操作
    is_batch_handle_allowed = True
    use_new_qa_modal = getattr(settings,'USE_NEW_QA_MODAL',False)

    return render(request,'operation_working_start.html',{
        'use_new_qa_modal':use_new_qa_modal,
        'l_m_manufacture_active':"active",
        'page_title':page_title,
        'source':"incasement",
        "is_batch_handle_allowed":is_batch_handle_allowed,
        'current_productionlines':current_productionlines,
    })

@login_required
def operation_working_period(request):
    '''
    单独的工作台: 时效
    '''
    mis_id_list = get_all_period_manu_items()

    # 第二步,找到 对应的 productionline
    productionline_id_list = get_batch_productionlines(batch_type="period")

    production_lines = ProductionLine.objects.filter(id__in=productionline_id_list)
    current_productionlines = []
    for pl in production_lines:
        if pl.is_show_in_operating_platform:
            current_manufacture_items = []
            for manufacture_item in pl.self_manufacture_items:
                if manufacture_item.id in mis_id_list:
                    current_manufacture_items.append(manufacture_item)
            # 有数据才显示
            if current_manufacture_items:
                one_node = {
                    'productionline':pl,
                    'manufacture_items':current_manufacture_items,
                }
                current_productionlines.append(one_node)
    page_title = _("period")

    # 是否允许批量操作，只有在 productionline 允许，下面变量为真的时候才显示批量操作
    is_batch_handle_allowed = True
    use_new_qa_modal = getattr(settings,'USE_NEW_QA_MODAL',False)

    return render(request,'operation_working_start.html',{
        'use_new_qa_modal':use_new_qa_modal,
        'l_m_manufacture_active':"active",
        'page_title':page_title,
        'source':"period",
        "is_batch_handle_allowed":is_batch_handle_allowed,
        'current_productionlines':current_productionlines,
    })


@login_required
def operation_working_other(request):
    '''
    单独的工作台: 其它

    说明：
        如果一个 ProductionLine ，不需要设备/设备id为0，且没有在 `检验`,`去毛刺`,`热处理`,`装箱`,`时效` 中显示，
        那么就在这里显示
    '''
    # 1. 找到不需要设备的工序记录
    # device_entry = DeviceEntry.objects.get(id=0)
    device_entry = get_object_or_none(DeviceEntry,id=0)
    ogrs = OperationGroupRecord.objects.filter(Q(device_items__isnull=True)|Q(device_items=device_entry))
    productionline_id_list = list(set([ogr.productionline.id for ogr in ogrs]))
    # 2. 排除上面的 `检验`,`去毛刺`,`热处理`,`装箱`,`时效` 等，只在 for 循环的时候排除
    mis_id_list = get_mis_id_list_other()

    production_lines = ProductionLine.objects.filter(id__in=productionline_id_list)

    current_productionlines = []
    for pl in production_lines:
        if pl.is_show_in_operating_platform:
            current_manufacture_items = []
            for manufacture_item in pl.self_manufacture_items:
                if manufacture_item.id in mis_id_list:
                    current_manufacture_items.append(manufacture_item)

            if current_manufacture_items:
                one_node = {
                    'productionline':pl,
                    'manufacture_items':current_manufacture_items,
                }
                current_productionlines.append(one_node)

    page_title = _("other")
    use_new_qa_modal = getattr(settings,'USE_NEW_QA_MODAL',False)

    return render(request,'operation_working_start.html',{
        'use_new_qa_modal':use_new_qa_modal,
        'l_m_manufacture_active':"active",
        'page_title':page_title,
        'current_productionlines':current_productionlines,
    })


@login_required
def batch_handle(request,productionline_id):
    '''
    视图功能：
        点击批量处理后，显示 批量处理 modal
        1. 如果是 自检/互检/检验 返回 attributes，交给用户填写测试值
        2. 其他则返回可以 完成的工件
    '''
    productionline = ProductionLine.objects.get(id=productionline_id)
    source = request.GET.get('source') if request.GET.get('source') else None

    if not productionline.is_batch_handle_allowed:
        messages.info(request,_("permission denied"))
        return HttpResponseRedirect(reverse('operation_working_start'))

    is_batch_check = False
    is_batch_wipe_burr = False
    is_batch_heattreatment = False
    is_batch_incasement = False
    is_batch_period = False

    # 需要批处理的 工件
    current_manufacture_items = []
    # 所有需要自检的 工件
    self_check_manufacture_items = []

    if source is None:
        # 必须指定来源，不然不知道是什么操作
        messages.info(request,_("modal source can not found"))
        return HttpResponseRedirect(request.META.get('HTTP_REFERER','/'))
    elif source == 'check':
        # 批量检验
        is_batch_check = True
        modal_title = _("batch check")
        mis_id_list = get_all_check_manu_items()
        for mi in productionline.self_manufacture_items:
            if mi.id in mis_id_list:
                temp_dict = {}
                temp_dict['manufacture_item'] = mi
                temp_dict['attributes'] = OperationAttribute.objects.filter(operation=mi.current_operation_record.operation)
                current_manufacture_items.append(temp_dict)
    elif source == 'wipe_burr':
        is_batch_wipe_burr = True
        modal_title = _("batch wipe burr")
        # 批量去毛刺
        mis_id_list = ManufactureItem.objects.filter(productionline__current_operation_record__oper_group_record__operation_group__name=u'去毛刺').values_list('id',flat=True)
        for mi in productionline.self_manufacture_items:
            if mi.id in mis_id_list:
                current_manufacture_items.append(mi)
    elif source == 'heattreatment':
        # 批量热处理
        is_batch_heattreatment = True
        modal_title = _("batch heattreatment")
        # 批量热处理
        mis_id_list = ManufactureItem.objects.filter(productionline__current_operation_record__oper_group_record__operation_group__name=u'热处理').values_list('id',flat=True)
        for mi in productionline.self_manufacture_items:
            if mi.id in mis_id_list:
                current_manufacture_items.append(mi)
    elif source == 'incasement':
        # 批量装箱
        is_batch_incasement = True
        modal_title = _("batch incasement")
        # 批量装箱
        mis_id_list = ManufactureItem.objects.filter(productionline__current_operation_record__oper_group_record__operation_group__name=u'装箱').values_list('id',flat=True)
        for mi in productionline.self_manufacture_items:
            if mi.id in mis_id_list:
                current_manufacture_items.append(mi)
    elif source == 'period':
        # 批量时效
        is_batch_period = True
        modal_title = _("batch period")
        # 批量时效
        mis_id_list = ManufactureItem.objects.filter(productionline__current_operation_record__oper_group_record__operation_group__name=u'时效').values_list('id',flat=True)
        for mi in productionline.self_manufacture_items:
            if mi.id in mis_id_list:
                current_manufacture_items.append(mi)
    else:
        # 不能识别的处理方式
        messages.info(request,_("unknow source type"))
        return HttpResponseRedirect(request.META.get('HTTP_REFERER','/'))


    # logger.info(current_manufacture_items)
    return render(request,'batch_handle.html',{
        'productionline':productionline,
        'modal_title':modal_title,
        'is_batch_check':is_batch_check,
        'is_batch_wipe_burr':is_batch_wipe_burr,
        'is_batch_heattreatment':is_batch_heattreatment,
        'is_batch_incasement':is_batch_incasement,
        'is_batch_period':is_batch_period,
        'current_manufacture_items':current_manufacture_items,
        'self_check_manufacture_items':self_check_manufacture_items,
    })


def create_qa_record_attribute(qa_record_id,attribute_id,current_operation_record,absolute_value):
    '''
    创建质检属性 -- add QARecordAttribute

    **参数**
    1. qa_record_id (QARecord)      质量记录 id
    2. attribute_id (Attribute)     属性 id
    3. absolute_value (float)       要求值
    '''
#--------------------------------------------------------------------------------------------------
    attribute = Attribute.objects.get(id=attribute_id)
    qa_record = QARecord.objects.get(id=qa_record_id)

    #create qa_record_attribute
    qa_record_attribute = QARecordAttribute(
        qa_record = qa_record,
        attribute = attribute,
        absolute_value = float(absolute_value),
    )

    #set qa_excessive_status
    difference = qa_record_attribute.absolute_value - float(qa_record_attribute.product_attribute.absolute_value)
    upper_deviation = float(qa_record_attribute.product_attribute.upper_deviation)
    lower_deviation = float(qa_record_attribute.product_attribute.lower_deviation)
    if difference > upper_deviation or difference < lower_deviation:
        qa_record_attribute.qa_excessive_status = 2
        if qa_record.qa_excessive_status != 2:
            qa_record.qa_excessive_status = 2
            qa_record.save()
        if current_operation_record.qa_excessive_status in [1,3]:
            current_operation_record.qa_excessive_status = 2
            current_operation_record.save()
    qa_record_attribute.save()
    return qa_record_attribute

def create_qa_record_new(employee,manufacture_item,attributes_list,qa_type):
    '''
    重写的 create_qa_record
    '''
    current_operation_record = manufacture_item.current_operation_record
    qa_record = QARecord.objects.create(
        employee         = employee,
        operation_record = current_operation_record,
        manufacture_item = manufacture_item,
        type             = qa_type,
    )
    # 创建质检属性
    for item_dict in attributes_list:
        value = item_dict.get('value')
        attribute_id = item_dict.get('attribute_id')
        create_qa_record_attribute(qa_record.id,attribute_id,current_operation_record,value)

    if qa_record.qa_excessive_status == 2:
        #generate code
        now = datetime.datetime.now()
        count = RejectProductRecord.objects.filter(date_added__startswith=now.date()).count()
        #create reject_product_record
        reject_product_record = RejectProductRecord(
            productionline    = qa_record.operation_record.oper_group_record.productionline,
            code              = '%s%03d' %(now.strftime('%Y%m%d'),count+1),
            qa_record         = qa_record,
            quality_problems  = '',
            reason_analysis   = '',
            processing_result = '',
        )
        reject_product_record.save()
    return qa_record


@login_required
def handle_batch_check(request):
    '''
    处理批量检验提交的数据
    1. 创建检验记录， 创建检验属性记录
    '''
    result_dict = {}
    if request.method == "POST":
        logger.info(request.POST)
        # attributes = request.POST.get('attributes') if request.POST.get('attributes') else None
        qualified_values = request.POST.get('qualified_values') if request.POST.get('qualified_values') else None
        # if attributes is None:
        #     result_dict['code'] = '1'
        #     result_dict['msg'] = ugettext_lazy('attributes does not exists')
        #     return HttpResponse(json.dumps(result_dict),content_type="application/json")

        # 检验结果，合格/不合格/稍后处理
        list_qualified_values = json.loads(qualified_values)
        for d in list_qualified_values:
            mi_id = d.get('mi_id')
            val = int(d.get('qualified_value'))
            mi = ManufactureItem.objects.get(id=mi_id)
            current_operation_record = mi.current_operation_record
            current_operation_record.quality_status = val
            current_operation_record.save()
            if val == 1:
                # 如果合格，mi进入下一个工步
                current_operation_record.qa_excessive_status = 3 # passed
                current_operation_record.save()
                mi.qa_excessive_status = 3 # passed
                mi.save()
                productionline_do_transition(request.user,mi.productionline,6)
            elif val == 2:
                # 不合格
                current_operation_record.qa_excessive_status = 4 # no_passed
                current_operation_record.status = 7 # error
                current_operation_record.save()
                mi.qa_excessive_status = 4 # no passed
                mi.status = 7  # error
                mi.save()
            else:
                # 稍后再处理
                pass

        # 解析 json 数据，重新封装
        # list_data = json.loads(attributes)
        # [
            # {u'attribute_id': 2, u'value': u'1', u'manufacture_item_id': 19}, 
            # {u'attribute_id': 3, u'value': u'10', u'manufacture_item_id': 19}, 
            # {u'attribute_id': 2, u'value': u'2', u'manufacture_item_id': 20}, 
            # {u'attribute_id': 2, u'value': u'3', u'manufacture_item_id': 21}
        # ]
        # 数据校验，输入的值必须是浮点数
        # for d in list_data:
        #     v = d.get('value')
        #     if v is None:
        #         result_dict['code'] = '1'
        #         result_dict['msg'] = ugettext("value must be required")
        #         return HttpResponse(json.dumps(result_dict),content_type="application/json")
        #     try:
        #         float(v)
        #     except Exception, e:
        #         result_dict['code'] = '1'
        #         result_dict['msg'] = ugettext('value must be a decimal number')
        #         return HttpResponse(json.dumps(result_dict),content_type="application/json")
        # 数据校验结束
        # result_list = []
        # mi_id_list = set([d.get('manufacture_item_id') for d in list_data])
        # # (19,20,21)
        # for mi_id in mi_id_list:
        #     temp_dict = {}
        #     temp_dict['mi_id'] = mi_id
        #     attributes_list = []
        #     for item in list_data:
        #         if item.get('manufacture_item_id') == mi_id:
        #             attributes_list.append(item)
        #     temp_dict['attributes_list'] = attributes_list
        #     result_list.append(temp_dict)
        # logger.info(result_list)
        # [{'attributes_list': [{u'attribute_id': 2,
        #     u'manufacture_item_id': 19,
        #     u'value': u'1'}],
        #   'mi_id': 19},
        #  {'attributes_list': [{u'attribute_id': 2,
        #     u'manufacture_item_id': 20,
        #     u'value': u'2'}],
        #   'mi_id': 20},
        #  {'attributes_list': [{u'attribute_id': 2,
        #     u'manufacture_item_id': 21,
        #     u'value': u'3'}],
        #   'mi_id': 21}]

        # user = User.objects.get(id=1)
        # employee = Employee.objects.get(user=user)
        # for item_dict in result_list:
        #     manufacture_item = ManufactureItem.objects.get(id=item_dict.get('mi_id'))
        #     current_operation_record = manufacture_item.current_operation_record
        #     qa_type = 1
        #     if current_operation_record.is_status_qa_inspector_record:
        #         qa_type = 3
        #     if current_operation_record.is_status_qa_double_record:
        #         qa_type = 2
        #     if current_operation_record.is_status_qa_self_record:
        #         qa_type = 1
        #     qa_record = create_qa_record_new(employee,manufacture_item,attributes_list,qa_type)

        #     if not qa_record.is_qa_excessive_status_excessive:
        #         # 必须由 质量部再次确认
        #         qa_record.set_qa_excessive_status_excessive()

        #     device_entry = None

        #     #find manufacture_record
        #     manufacture_records = ManufactureRecord.objects.filter(
        #         manufacture_item = manufacture_item,
        #         operation_record = current_operation_record,
        #         device_entry     = device_entry
        #     ).order_by('-date_added')
        #     if len(manufacture_records) > 0:
        #         #end timesheet
        #         end_timesheet(employee,manufacture_records[0])

        result_dict['code'] = '0'
        result_dict['msg'] = 'success'
        return HttpResponse(json.dumps(result_dict),content_type="application/json")


def handle_batch_work_finished(request):
    '''
    批量处理  - '工作'完成
    '''
    result_dict = {}
    if request.method == "POST":
        logger.info(request.POST)
        mis = request.POST.getlist('mis') if request.POST.getlist('mis') else None
        note = request.POST.get('note') if request.POST.get('note') else ''
        # 获得需要处理的所有工件
        if mis is None:
            result_dict['code'] = '1'
            result_dict['msg'] = 'any manufactureitems need process'
            return HttpResponse(json.dumps(result_dict),content_type="application/json")

        # 处理工件
        temp_batch_ts = datetime.datetime.now()
        for mi_id in mis:
            handle_manu_item_finished(
                user=request.user,
                mi_id=mi_id,
                note=note,
                temp_batch_ts=temp_batch_ts,
                device_entry_id=None)

        result_dict['code'] = '0'
        result_dict['msg'] = 'success'
        return HttpResponse(json.dumps(result_dict),content_type="application/json")
    else:
        result_dict['code'] = '1'
        result_dict['msg'] = 'invalid method'
        return HttpResponse(json.dumps(result_dict),content_type="application/json")


def handle_manu_item_finished(user,mi_id,note,temp_batch_ts,device_entry_id=None):
    '''
    处理单个工件结束
    '''
    result = 0
    manufacture_item = ManufactureItem.objects.get(id=mi_id)
    current_operation_record = manufacture_item.current_operation_record

    # 记录批量处理的 ： 处理人，备注信息，处理时间
    current_operation_record.temp_batch_note = note
    current_operation_record.temp_batch_ts = temp_batch_ts
    current_operation_record.temp_batch_operator = user
    current_operation_record.save()

    if device_entry_id is not None:
        device_entry = DeviceEntry.objects.get(id=device_entry_id)
    else:
        device_entry = None

    # 因为要标识为工作结束，所以这里 status 必须为 6
    status = 6
    manufacture_item.status = status
    manufacture_item.save()
    logger.info(manufacture_item.status)

    u = User.objects.get(id=1)
    employee = Employee.objects.get(user=u)

    #find manufacture_record
    manufacture_records = ManufactureRecord.objects.filter(
        manufacture_item = manufacture_item,
        operation_record = current_operation_record,
        device_entry     = device_entry
    ).order_by('-date_added')
    if len(manufacture_records) > 0:
        #end timesheet
        end_timesheet(employee,manufacture_records[0])

    result = productionline_do_transition(user,manufacture_item.productionline,6)
    return result



#--------------------------------------------------------------------------------------------------
# 新的处理流程
def handle_new_flow_check_qa_record(request):
    '''
    函数说明：
        处理新的检验流程中的自检和互检

    参数：
        1. mi_id        工件id
        2. attributes   属性值列表，包含工件各个属性的测量值
        3. qa_type      检测类型，qa_type 为1表示自检，为2表示互检
    处理任务：
        1. 创建一个 QARecord
        2. 创建多个 QARecordAttribute
    '''
    result = 0
    if request.method == "POST":
        logger.info(request.POST)

        # 1. 工件id
        mi_id = request.POST.get('mi_id')
        # 2. 属性
        attributes = request.POST.get('attributes') if request.POST.get('attributes') else None
        # 3. 类型： 自检/互检
        qa_type = request.POST.get('qa_type')
        # 4. 发送到质量部？
        report_to_qa_dept = request.POST.get('is_report_to_qa_dept',False)
        if int(report_to_qa_dept) == 1:
            is_report_to_qa_dept = True
        else:
            is_report_to_qa_dept = False
        # 5. 备注
        check_note = request.POST.get('note','')
        # 6. 检验人
        surveyor = request.POST.get('surveyor','')

        # 数据校验
        # mi_id 必须
        # attributes 必须
        # qa_type 必须
        # is_report_to_qa_dept 有默认值，非必须
        # check_note ， surveyor 可选填

        # 获取数据
        mi = ManufactureItem.objects.get(id=mi_id)

        user = User.objects.get(id=1)
        employee = Employee.objects.get(user=user)

        attributes_list = json.loads(attributes) if attributes else []
        for d in attributes_list:
            v = d.get('value')
            if v is None:
                result = 1
                _msg = ugettext('value must be required')
                data   = {'result':result,'msg':msg[result],'state':_msg,}
                return HttpResponse('yuankong(' + json.dumps(data) + ');', content_type="application/json")
            try:
                float(v)
            except Exception:
                result = 1
                _msg = ugettext('value must be a decimal number')
                data   = {'result':result,'msg':msg[result],'state':_msg,}
                return HttpResponse('yuankong(' + json.dumps(data) + ');', content_type="application/json")

        if attributes_list:
            qa_record = create_qa_record_with_new_check_flow(
                employee=employee,
                manufacture_item=mi,
                attributes_list=attributes_list,
                qa_type=qa_type,
                check_note=check_note,
                surveyor=surveyor,
                is_report_to_qa_dept=is_report_to_qa_dept,
            )

        data = {'result':result,'msg':msg[result],'state':state[result],}
        return HttpResponse('yuankong(' + json.dumps(data) + ');', content_type="application/json")
    else:
        result = 1
        data = {'result':result,'msg':msg[result],'state':state[result],}
        return HttpResponse('yuankong(' + json.dumps(data) + ');', content_type="application/json")


def create_qa_record_with_new_check_flow(employee,manufacture_item,attributes_list,qa_type,check_note,surveyor,is_report_to_qa_dept=False):
    '''
    创建 自检/互检 记录
    '''
    current_operation_record = manufacture_item.current_operation_record
    qa_record = QARecord.objects.create(
        employee         = employee,
        operation_record = current_operation_record,
        manufacture_item = manufacture_item,
        type             = int(qa_type),          # 1.自检(type=1)/互检(type=2)
        check_note       = check_note,            # 备注
        surveyor_string  = surveyor,              # 检验人
    )
    # 如果用户选择了报质量部，则转到质量部
    if is_report_to_qa_dept:
        qa_record.qa_excessive_status = 2
        qa_record.save()
        # 不加这个，质量部看不到
        manufacture_item.qa_excessive_status = 5
        manufacture_item.save()
    # 创建质检属性
    for item_dict in attributes_list:
        value = item_dict.get('value')
        attribute_id = item_dict.get('attribute_id')
        attribute = Attribute.objects.get(id=attribute_id)
        # create_qa_record_attribute(qa_record.id,attribute_id,current_operation_record,value)
        qa_record_attribute = QARecordAttribute(
            qa_record = qa_record,
            attribute = attribute,
            absolute_value = float(value),
        )
        difference = qa_record_attribute.absolute_value - float(qa_record_attribute.product_attribute.absolute_value)
        upper_deviation = float(qa_record_attribute.product_attribute.upper_deviation)
        lower_deviation = float(qa_record_attribute.product_attribute.lower_deviation)
        logger.info("difference={0},upper_deviation={1},lower_deviation={2}".format(difference,upper_deviation,lower_deviation))
        if (not (abs(difference - upper_deviation) < 0.00001)) or (not (abs(lower_deviation - difference) < 0.00001)):
            qa_record_attribute.qa_excessive_status = 2
            # 如果互检，发现值不对，提交到质量部, 工件暂停
            if qa_record.is_type_qa_double_check_record and not qa_record.is_qa_excessive_status_excessive:
                qa_record.qa_excessive_status = 2
                qa_record.save()

        # 保存 qa_record_attribute
        qa_record_attribute.save()

    return qa_record

@login_required
def handle_operation_finish(request):
    '''
    函数说明：
        某个工件直接完成该工步
    '''
    result = 0
    user = User.objects.get(id=1)
    employee = Employee.objects.get(user=user)
    if request.method == 'POST':
        # 1. 工件id
        item_code = request.POST.get('item_code')
        manufacture_item = ManufactureItem.objects.get(code=item_code)
        device_entry_id = int(request.POST['device_entry_id'])
        device_entry = DeviceEntry.objects.get(id=device_entry_id)
        current_operation_record = manufacture_item.current_operation_record

        # 直接结束
        status = 6
        manufacture_item.status = status
        # manufacture_item.save()

        # 处理检验状态： 1.如果有历史自检/互检/检验数据，修改 工件状态为 passed 2. 如果没有，状态设置为 normal
        if manufacture_item.self_records.all().exists():
            manufacture_item.qa_excessive_status = 3          # passed
        else:
            manufacture_item.qa_excessive_status = 1          # normal
        manufacture_item.save()

        #find manufacture_record
        manufacture_records = ManufactureRecord.objects.filter(
            manufacture_item = manufacture_item,
            operation_record = current_operation_record,
            device_entry     = device_entry
        ).order_by('-date_added')
        if len(manufacture_records) > 0:
            #end timesheet
            end_timesheet(employee,manufacture_records[0])

        #do_transition
        if manufacture_item.status == 6:
            result = productionline_do_transition(request.user,manufacture_item.productionline,6)


    data   = {'result':result,'msg':msg[result],'state':state[result],}
    return HttpResponse('yuankong(' + json.dumps(data) + ');', content_type="application/json")


@login_required
def handle_qualified(request):
    result = 0
    if request.method == "POST":
        mi_id = request.POST.get('mi_id')
        val = int(request.POST.get('value'))

        mi = ManufactureItem.objects.get(id=mi_id)
        current_operation_record = mi.current_operation_record
        current_operation_record.quality_status = val
        current_operation_record.save()

        if val == 1:
            # 如果合格，mi进入下一个工步
            current_operation_record.qa_excessive_status = 3 # passed
            current_operation_record.save()
            mi.qa_excessive_status = 3 # passed
            mi.save()
            productionline_do_transition(request.user,mi.productionline,6)
        elif val == 2:
            # 不合格
            current_operation_record.qa_excessive_status = 4 # no_passed
            current_operation_record.status = 7 # error
            current_operation_record.save()
            mi.qa_excessive_status = 4 # no passed
            mi.status = 7  # error
            mi.save()
        else:
            # 稍后再处理
            pass
    data   = {'result':result,'msg':msg[result],'state':state[result],}
    return HttpResponse('yuankong(' + json.dumps(data) + ');', content_type="application/json")

@login_required
def show_new_qa_modal(request,mi_id):
    '''
    函数说明：
        如果 settings 中的 USE_NEW_QA_MODAL 为 True
            `生产部`->`工作台`->`其它` 原有的质检记录改由 modal 来显示
        如果 settings 中的 USE_NEW_QA_MODAL 为 False
            质检记录在 `工作`按钮之后连续显示
    '''
    mi = ManufactureItem.objects.get(id=mi_id)
    return render(request,'show_new_qa_modal.html',{
        'mi':mi,
    })
#--------------------------------------------------------------------------------------------------