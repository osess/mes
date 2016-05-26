#-*- coding: UTF-8 -*- 
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.decorators import login_required
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ugettext
import json
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



# 删除 operation_group 对应的 工艺卡
@login_required
def ajax_delete_technology_file(request):
    d = {}
    if request.method == "POST":
        operation_group_id = request.POST.get('operation_group','')
        if operation_group_id.strip() == '':
            d['code'] = '1'
            d['msg'] = 'operation_group id must be required'
            return HttpResponse(json.dumps(d),content_type="application/json")
        operation_group = OperationGroup.objects.get(id=operation_group_id)
        TU1_file = operation_group.TU1_file
        TU2_file = operation_group.TU2_file
        TU3_file = operation_group.TU3_file

        if TU1_file:
            TU1_file.set_file_to_delete()
        if TU2_file:
            TU2_file.set_file_to_delete()
        if TU3_file:
            TU3_file.set_file_to_delete()
        d['code'] = '0'
        d['msg'] = 'success'
        return HttpResponse(json.dumps(d),content_type="application/json")
    else:
        d['code'] = '1'
        d['msg'] = 'invalid method'
        return HttpResponse(json.dumps(d),content_type="application/json")


@login_required
def ajax_set_operation_not_required(request):
    """
    函数说明：
        `技术部`->`工艺列表`->`审核记录`
        将创建工步属性由`可能`修改为`不需要`
    """
    d = {}

    if request.method == "POST":
        operation_id = request.POST.get('operation_id','')
        if operation_id is None or operation_id.strip() == '':
            d['code'] = '1'
            d['msg'] = ugettext("operation id must be required")
            return HttpResponse(json.dumps(d),content_type="application/json")
        try:
            operation = Operation.objects.get(id=operation_id)
            operation.set_need_attribute_not_required()
            d['code'] = '0'
            d['msg'] = 'success'
            return HttpResponse(json.dumps(d),content_type="application/json")
        except Exception, e:
            d['code'] = '1'
            d['msg'] = ugettext('unknow error')
            return HttpResponse(json.dumps(d),content_type="application/json")
    else:
        d['code'] = '1'
        d['msg'] = 'invalid method'
        return HttpResponse(json.dumps(d),content_type="application/json")