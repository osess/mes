#-*- coding: UTF-8 -*- 
from django.shortcuts import render_to_response
from django.shortcuts import render
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import auth
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ugettext
from django.utils.simplejson.encoder import JSONEncoder
import json
import datetime
#from thirdparty
#from workflows.models import
from workflows.models import State
from workflows.utils import *
from permissions.utils import *
#from xxd
from yt_timesheet.models import Timesheet
from technologies.models import Technology, OperationGroup, Operation
from person.models import Employee
#from lxy
from manufactureplan.models import *
from productcatalog.models import Attribute
#from device.models import DeviceItem
from django.utils.log import logger
from manufactureplan.utils import productionline_do_transition

@login_required
def excessive_qa_records_list(request):
    manufacture_items = []
    if request.user.has_perm('manufactureplan.quality_manufactureitem'):
        manufacture_items = [item for item in ManufactureItem.objects.exclude(qa_excessive_status=1)]
    return render_to_response('excessive_qa_records_list.html', {
        'manufacture_items':manufacture_items,
        'l_m_qa_active':"active",
    }, context_instance=RequestContext(request))

@login_required
def wait_excessive_qa_records_list(request):
    '''
    质检问题列表 --待处理
    '''
    wait_manufacture_items = []
    if request.user.has_perm('manufactureplan.quality_manufactureitem'):
        for manufacture_item in ManufactureItem.objects.exclude(qa_excessive_status=1):
            # qa_excessive_status != 1 且 qa_excessive_status == 2
            if manufacture_item.self_records.filter(qa_excessive_status=2):
                wait_manufacture_items.append(manufacture_item)
            # for excessive_qa_record in manufacture_item.excessive_qa_records:
            #     if excessive_qa_record.item_wait:
            #         wait_manufacture_items.append(manufacture_item)
            #         break
    return render_to_response('excessive_qa_records_list.html', {
        'manufacture_items':wait_manufacture_items,
        'l_m_qa_active':"active",
    }, context_instance=RequestContext(request))

@login_required
def pass_excessive_qa_records_list(request):
    pass_manufacture_items = []
    if request.user.has_perm('manufactureplan.quality_manufactureitem'):
        for manufacture_item in ManufactureItem.objects.exclude(qa_excessive_status=1):
            for excessive_qa_record in manufacture_item.excessive_qa_records:
                if excessive_qa_record.item_pass:
                    pass_manufacture_items.append(manufacture_item)
                    break
    return render_to_response('excessive_qa_records_list.html', {
        'manufacture_items':pass_manufacture_items,
        'l_m_qa_active':"active",
    }, context_instance=RequestContext(request))

@login_required
def fail_excessive_qa_records_list(request):
    fail_manufacture_items = []
    if request.user.has_perm('manufactureplan.quality_manufactureitem'):
        for manufacture_item in ManufactureItem.objects.exclude(qa_excessive_status=1):
            for excessive_qa_record in manufacture_item.excessive_qa_records:
                if excessive_qa_record.item_fail:
                    fail_manufacture_items.append(manufacture_item)
                    break
    return render_to_response('excessive_qa_records_list.html', {
        'manufacture_items':fail_manufacture_items,
        'l_m_qa_active':"active",
    }, context_instance=RequestContext(request))

@login_required
def excessive_qa_record_view(request,qa_record_id):
    redirecturl = request.REQUEST.get('next','')
    qa_record = None
    qa_record_attributes = []
    if request.user.has_perm('manufactureplan.quality_manufactureitem'):
        qa_record = QARecord.objects.get(id=qa_record_id)
        qa_record_attributes = QARecordAttribute.objects.filter(qa_record=qa_record)
    return render_to_response('excessive_qa_record_view.html', {
        'qa_record':qa_record,'qa_record_attributes':qa_record_attributes,'redirecturl':redirecturl, 'l_m_qa_active':"active",
    }, context_instance=RequestContext(request))
    

@login_required
def ajax_excessive_qa_record_fail(request):
    '''
    质量部，自检失败
    用户自检之后，提交到质量部，质量部检查未通过
    '''
    result = 0
    msg = {0:'success'}
    if request.method == 'POST':
        qa_record_id = int(request.POST['qa_record_id'])
        qa_record = QARecord.objects.get(id=qa_record_id)
        quality_problems_note = request.POST['quality_problems_note']
        reason_analysis_note = request.POST['reason_analysis_note']
        processing_result_note = request.POST['processing_result_note']

        #set reject_product_record attributes
        reject_product_record = qa_record.self_reject_product_record
        if reject_product_record:
            reject_product_record.quality_problems = quality_problems_note
            reject_product_record.reason_analysis = reason_analysis_note
            reject_product_record.processing_result = processing_result_note
            reject_product_record.save()

        #set qa_record.qa_excessive_status
        qa_record.qa_excessive_status = 4
        qa_record.decider = request.user
        qa_record.save()

    data = {'result':result,'msg':msg[result]}
    return HttpResponse('yuankong(' + json.dumps(data) + ');', content_type="application/json")

@login_required
def ajax_decision_fail_qa_record(request):
    result = 0
    msg = {0:'success'}
    if request.method == 'POST':
        qa_record_id = int(request.POST['qa_record_id'])
        qa_record = QARecord.objects.get(id=qa_record_id)
        todo_type = int(request.POST['todo_type'])
        
        reject_product_record = qa_record.self_reject_product_record
        reject_product_record.todo_type = todo_type
        reject_product_record.decider = request.user
        reject_product_record.save()

    data = {'result':result,'msg':msg[result]}
    return HttpResponse('yuankong(' + json.dumps(data) + ');', content_type="application/json")


@login_required
def ajax_excessive_qa_record_pass(request):
    '''
    自检通过
    用户自检之后，提交到质量部，质量部检查通过
    ''' 
    result = 0
    msg = {0:'success'}
    if request.method == 'POST':
        qa_record_id = int(request.POST['qa_record_id'])
        qa_record    = QARecord.objects.get(id=qa_record_id)
        note         = request.POST['pass_note']

        #create_new_manufacture_item(qa_record.manufacture_item,'pass')
        logger.info(qa_record)
        #set reject_product_record attributes
        reject_product_record = qa_record.self_reject_product_record
        if reject_product_record:
            reject_product_record.quality_problems = note
            reject_product_record.reason_analysis = ''
            reject_product_record.processing_result = 'pass'
            reject_product_record.save()

        #set qa_record.qa_excessive_status
        qa_record.qa_excessive_status = 3
        qa_record.note = note
        qa_record.decider = request.user
        qa_record.save()
        logger.info(qa_record)

        #do_transition
        # 结束
        manufacture_item = qa_record.manufacture_item
        # 如果工件的检验记录都合格了，则修改为通过
        number_of_qa_records = len(manufacture_item.excessive_qa_records)
        number_of_qa_records_passed = 0
        for qa in manufacture_item.excessive_qa_records:
            if qa.item_pass:
                number_of_qa_records_passed += 1
        if number_of_qa_records == number_of_qa_records_passed:
            manufacture_item.qa_excessive_status = 3
            manufacture_item.save()

        if manufacture_item.status == 6:
            result = productionline_do_transition(request.user,manufacture_item.productionline,6)

    data = {'result':result,'msg':msg[result]}
    return HttpResponse('yuankong(' + json.dumps(data) + ');', content_type="application/json")


def create_new_manufacture_item(manufacture_item,code_tag):
    #create new production_line, signal create new manu_item_group
    production_line = manufacture_item.manu_item_group.productionline
    production_line_new = ProductionLine(
        #code          = production_line.code + code_tag + manufacture_item.code,
        #name          = production_line.name,
        technology    = production_line.technology,
        #start_time    = production_line.start_time,
        #finish_time   = production_line.finish_time,
        state         = 5,
    )
    production_line_new.save()
    #create new manu_item_group
    manu_item_group = manufacture_item.manu_item_group
    manu_item_group_new = ManufactureItemGroup(
        product             = manu_item_group.product,
        quantity            = 1,
        productionline      = production_line_new,
        manufactureplan     = manu_item_group.manufactureplan,
    )
    manu_item_group_new.save()
    #create new manufacture_item
    manufactureitem_new = ManufactureItem(
        code = code_tag + manufacture_item.code,
        manu_item_group = manu_item_group_new,
        batch_code = manu_item_group_new.batch_code,
        status = manufacture_item.status + 1,
    )
    manufactureitem_new.save()
    #create new oper_group_records
    for oper_group_record in production_line.oper_group_records.all():
        oper_group_record_new = OperationGroupRecord(
            #code            = oper_group_record.code + code_tag + manufacture_item.code,
            productionline  = production_line_new,
            operation_group = oper_group_record.operation_group,
            #job             = oper_group_record.job,
        )
        oper_group_record_new.save()
        for device_item in oper_group_record.device_items.all():
            oper_group_record_new.device_items.add(device_item)
        oper_group_record_new.save()
        #create new operation_records
        for operation_record in oper_group_record.operation_records.all():
            operation_record_new = OperationRecord(
                #code               = operation_record.code + code_tag + manufacture_item.code,
                oper_group_record  = oper_group_record_new,
                operation          = operation_record.operation,
                #employee           = operation_record.employee,
            )
            operation_record_new.save()
            for knife_item in operation_record.knife_items.all():
                operation_record_new.knife_items.add(knife_item)
            for tool_item in operation_record.tool_items.all():
                operation_record_new.tool_items.add(tool_item)
            operation_record_new.save()

    #set workflow
    workflow = production_line_new.technology.workflow
    set_workflow(production_line_new,workflow)
    #set state
    current_state = get_state(production_line)
    set_state(production_line_new,current_state)
    #set operation_record status
    current_operation_record = production_line_new.current_operation_record
    current_operation_record.status = manufacture_item.status + 1
    current_operation_record.save()


@login_required
def ajax_qa_record_attribute_decision(request):
    from manufactureplan.views import productionline_do_transition, find_current_operation_record
    result = 0
    msg = {0:'success'}
    if request.method == 'POST':
        qa_record_attribute_id = request.POST['qa_record_attribute_id']
        note = request.POST['note']
        type = request.POST['type']
        qa_record_attribute = QARecordAttribute.objects.get(id=qa_record_attribute_id)
        qa_record_attribute.qa_excessive_status = int(type)
        qa_record_attribute.note = note
        qa_record_attribute.decide_people = request.user
        qa_record_attribute.save()

        #set current_operation_record.QA_status
        status = find_current_operation_record(qa_record_attribute.qa_record.manufacture_item).QA_status

        manu_item_group = qa_record_attribute.qa_record.manufacture_item.manu_item_group
        if manu_item_group.QA_status == 6 and manu_item_group.current_manufacture_items_decided:
            if manu_item_group.current_manufacture_items_passed:
                productionline_do_transition(request.user,manu_item_group.productionline,6)
            else:
                productionline_do_transition(request.user,manu_item_group.productionline,7)

    data = {'result':result,'msg':msg[result]}
    return HttpResponse('yuankong(' + json.dumps(data) + ');', content_type="application/json")


@login_required
def qa_record_list(request):
    '''
    函数说明：
        1.返回所有 `工件`的 qa 记录
        2. 允许用户查询 `工件` code 对应工件 的 qa 记录
    '''
    if request.method == "POST":
        q = request.POST.get('q','')
        if q.strip() == "":
            mis = ManufactureItem.objects.none()
            return render(request,'qa_record_list.html',{
                "mis":mis,
            })
        mis = ManufactureItem.objects.filter(code__contains=q.strip())
        return render(request,'qa_record_list.html',{
            "mis":mis,
            "q":q,
            'title':ugettext("%(query_string)s 's qa record list") % {"query_string":q},
        })
    else:
        mis = ManufactureItem.objects.none()
        return render(request,'qa_record_list.html',{
            "mis":mis,
        })


@login_required
def blank_no_passed_list(request):
    '''
    函数说明：
        返回所有毛坯检验不合格的`工件`
    '''
    queryset = ManufactureItem.objects.filter(productionline__current_operation_record__quality_status=2)

    if request.method == "POST":
        q = request.POST.get('q','')
        if q.strip() == "":
            mis = ManufactureItem.objects.none()
            return render(request,'blank_no_passed_list.html',{
                "mis":mis,
            })
        mis = queryset.filter(code__contains=q.strip())
        return render(request,'blank_no_passed_list.html',{
            "mis":mis,
            "q":q,
            'title':ugettext("%(query_string)s 's blank no passed list") % {"query_string":q},
        })
    else:
        return render(request,'blank_no_passed_list.html',{
            "mis":queryset,
        })