#-*- coding:utf-8 -*-
from django.shortcuts import render_to_response, get_object_or_404, render
from django.shortcuts import redirect
from django.http import HttpResponse
from django.template import RequestContext, loader, Context
from django.template.response import TemplateResponse

from django.utils.translation import ugettext_lazy as _
from xadmin.plugins.actions import BaseActionView

import base64
from hubarcode.code128 import Code128Encoder
from yt_barcode.models import Barcode
from yt_barcode.views import add_barcode
from technologies.models import Technology
from manufactureplan.models import *
from settings import TECHNOLOGY_REPORT_ROW, UPLOAD_ROOT
from constance import config

####################################
#extjs report, by xxd
####################################
from django.contrib.auth.decorators import login_required
from django.utils.simplejson.encoder import JSONEncoder
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.urlresolvers import reverse
from django.db.models import Count
from datetime import datetime, timedelta
from warehouse.models import *

from yt_timesheet.models import *

DATETIMEFORMAT = '%Y-%m-%d %H:%M:%S'

@login_required
def ext_manufactureitem_working_time(request, template_name="ext_manufactureitem_working_time.html"):
    title = _("manufactureitem_working_time")
    manufacture_items = []
    extra_context = {'manufacture_items': manufacture_items,'title':title}
    return render(request, template_name, extra_context)

@login_required
def json_ext_manufactureitem_working_time(request):
    manu_item_groups = ManufactureItemGroup.objects.filter(productionline__isnull=False).order_by('manufactureplan')
    manufacture_items = ManufactureItem.objects.all()

    json = {}
    data = []
    total = manu_item_groups.count()
    json['totalCount'] = total

    func = request.GET.get("func", None)
    page  = request.GET.get("page", None)
    limit = request.GET.get("limit", None)
    if func and func == '2':
        timesheets = Timesheet.objects.filter(content_type__model='manufacturerecord')
        for i in range(12):
            aaa = {'month': _("%d month") % (i+1)}
            ies_timesheets = timesheets.filter(start__month=i+1).order_by('-start')
            timesheets = timesheets.exclude(start__month=i+1).order_by('-start')
            worked_hours = sum([t.difference_hours for t in ies_timesheets],timedelta())
            aaa['cNum'] = worked_hours.seconds
            data.append(aaa)
        response = HttpResponse(content=JSONEncoder().encode(data),
                    mimetype='text/javascript')
    else:
        if page and limit:
            paginator = Paginator(manu_item_groups, int(limit))
            try:
                manu_item_groups = paginator.page(int(page))
            except PageNotAnInteger:
                # If page is not an integer, deliver first page.
                manu_item_groups = paginator.page(int(page))
            except EmptyPage:
                # If page is out of range (e.g. 9999), deliver last page of results.
                manu_item_groups = paginator.page(paginator.num_pages)
        i = 1
        for mig in manu_item_groups:
            aaa = {'i': i}
            aaa['cc'] = mig.manufactureplan.order.contract_code
            aaa['mc'] = mig.id
            aaa['pn'] = '<a href="'+reverse('ext_manufactureitem_working_time_detail',args=[mig.id])+'">'+ mig.product.name +'</>'
            aaa['qty'] = mig.quantity
            aaa['pcc'] = mig.product.cad_code
            aaa['s'] = mig.productionline.get_state_display()
            aaa['wh'] = str(timedelta(seconds=sum([mi.worked_hours for mi in mig.manufacture_items.all()],timedelta()).seconds))
            data.append(aaa)
            i += 1

        json['data'] = data
        response = HttpResponse(content=JSONEncoder().encode(json),
                        mimetype='text/javascript')
    response['Content-Length'] = len(response.content)
    return response

@login_required
def ext_manufactureitem_working_time_detail(request, mig_id, template_name="ext_manufactureitem_working_time_detail.html"):
    mig = ManufactureItemGroup.objects.get(id=mig_id)
    title = _("manufactureitem_working_time_detail %s") % mig.product.name
    extra_context = {'mig_id': mig_id,'title':title}
    return render(request, template_name, extra_context)

@login_required
def json_ext_manufactureitem_working_time_detail(request, mig_id):
    mig = ManufactureItemGroup.objects.get(id=mig_id)
    mis_id = [mi.id for mi in mig.manufacture_items.all()]
    mrs_id = [mr.id for mr in ManufactureRecord.objects.filter(manufacture_item_id__in=mis_id)]
    timesheets = Timesheet.objects.filter(object_id__in=mrs_id,content_type__model='manufacturerecord')
    
    json = {}
    data = []
    total = timesheets.count()
    json['totalCount'] = total

    func = request.GET.get("func", None)
    page  = request.GET.get("page", None)
    limit = request.GET.get("limit", None)
    if func and func == '2':
        i_timesheets = timesheets
        for i in range(12):
            aaa = {'month': _("%d month") % (i+1)}
            ies_timesheets = timesheets.filter(start__month=i+1).order_by('-start')
            i_timesheets = i_timesheets.exclude(start__month=i+1).order_by('-start')
            worked_hours = sum([t.difference_hours for t in ies_timesheets],timedelta())
            aaa['cNum'] = worked_hours.seconds
            data.append(aaa)
        response = HttpResponse(content=JSONEncoder().encode(data),
                    mimetype='text/javascript')
    else:
        if page and limit:
            paginator = Paginator(timesheets, int(limit))
            try:
                timesheets = paginator.page(int(page))
            except PageNotAnInteger:
                # If page is not an integer, deliver first page.
                timesheets = paginator.page(int(page))
            except EmptyPage:
                # If page is out of range (e.g. 9999), deliver last page of results.
                timesheets = paginator.page(paginator.num_pages)

        for ts in timesheets:
            aaa = {'mi':ts.content_object.manufacture_item.__unicode__()}
            aaa['start'] = ts.start.strftime(DATETIMEFORMAT)
            aaa['end'] = ts.end.strftime(DATETIMEFORMAT)
            aaa['df'] = str(timedelta(seconds=ts.difference_hours.seconds))
            aaa['type'] = ts.get_type_display()
            data.append(aaa)

        json['data'] = data
        response = HttpResponse(content=JSONEncoder().encode(json),
                        mimetype='text/javascript')
    response['Content-Length'] = len(response.content)
    return response

    
@login_required
def ext_employee_worked_manufactureitem(request, template_name="ext_employee_worked_manufactureitem.html"):
    title = _("employee_worked_manufactureitem")
    timesheets = Timesheet.objects.filter(content_type__model='manufacturerecord')
    starts = timesheets.values('start').annotate(Count('start')).order_by('start')
    years = sorted(list(set([start['start'].year for start in starts])), reverse = True)
    extra_context = {'years': years,'title':title}
    return render(request, template_name, extra_context)

@login_required
def json_ext_employee_worked_manufactureitem(request, year):
    now = datetime.now()
    employees = Employee.objects.filter(department_id=2)
    timesheets = Timesheet.objects.filter(start__year=year,content_type__model='manufacturerecord')

    json = {}
    data = []
    total = employees.count()
    json['totalCount'] = total

    func = request.GET.get("func", None)
    page  = request.GET.get("page", None)
    limit = request.GET.get("limit", None)
    if page and limit:
        paginator = Paginator(employees, int(limit))
        try:
            employees = paginator.page(int(page))
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            employees = paginator.page(int(page))
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            employees = paginator.page(paginator.num_pages)

    for e in employees:
        e_name = e.name if func and func == '2' else '<a href="'+reverse('ext_employee_worked_detail',args=[e.id])+'">'+ e.name +'</>'
        aaa = {0:e_name}
        ts = timesheets.filter(person=e)
        for i in range(12):
            if datetime(int(year),i+1,1) > now:
                aaa[i+1] = 0 if func and func == '2' else '-'
            else:
                e_ts = ts.filter(start__month=i+1)
                ts = ts.exclude(start__month=i+1)
                mrs_id = [e.object_id for e in e_ts]
                mrs = ManufactureRecord.objects.filter(id__in=mrs_id)
                mi_count = mrs.values('manufacture_item').annotate(Count('manufacture_item')).count()
                aaa[i+1] = mi_count
        data.append(aaa)
    if func and func == '2':
        response = HttpResponse(content=JSONEncoder().encode(data),
                    mimetype='text/javascript')
    else:
        json['data'] = data
        response = HttpResponse(content=JSONEncoder().encode(json),
                    mimetype='text/javascript')
    response['Content-Length'] = len(response.content)
    return response

@login_required
def ext_employee_worked_detail(request, employee_id, template_name="ext_employee_worked_detail.html"):
    employee = Employee.objects.get(id=employee_id)
    title = _("employee_worked_detail %s") % employee.name
    extra_context = {'employee_id':employee_id,'title':title}
    return render(request, template_name, extra_context)

@login_required
def json_ext_employee_worked_detail(request, employee_id):
    employee = Employee.objects.get(id=employee_id)
    timesheets = Timesheet.objects.filter(person=employee,content_type__model='manufacturerecord')

    json = {}
    data = []
    total = timesheets.count()
    json['totalCount'] = total

    func = request.GET.get("func", None)
    page  = request.GET.get("page", None)
    limit = request.GET.get("limit", None)

    if func and func == '2':
        for i in range(12):
            aaa = {'month': _("%d month") % (i+1)}
            e_ts = timesheets.filter(start__month=i+1)
            timesheets = timesheets.exclude(start__month=i+1)
            worked_hours = sum([t.difference_hours for t in e_ts],timedelta())
            aaa['cNum'] = worked_hours.seconds
            data.append(aaa)
        response = HttpResponse(content=JSONEncoder().encode(data),
                        mimetype='text/javascript')
    else:
        if page and limit:
            paginator = Paginator(timesheets, int(limit))
            try:
                timesheets = paginator.page(int(page))
            except PageNotAnInteger:
                # If page is not an integer, deliver first page.
                timesheets = paginator.page(int(page))
            except EmptyPage:
                # If page is out of range (e.g. 9999), deliver last page of results.
                timesheets = paginator.page(paginator.num_pages)
        for ts in timesheets:
            aaa = {'mi':ts.content_object.manufacture_item.__unicode__()}
            aaa['start'] = ts.start.strftime(DATETIMEFORMAT)
            aaa['end'] = ts.end.strftime(DATETIMEFORMAT)
            aaa['df'] = str(timedelta(seconds=ts.difference_hours.seconds))
            aaa['type'] = ts.get_type_display()
            data.append(aaa)
        json['data'] = data
        response = HttpResponse(content=JSONEncoder().encode(json),
                        mimetype='text/javascript')

    response['Content-Length'] = len(response.content)
    return response

@login_required
def ext_device_working_time(request, template_name="ext_device_working_time.html"):
    title = _("device_working_time")
    timesheets = Timesheet.objects.filter(content_type__model='manufacturerecord')
    starts = timesheets.values('start').annotate(Count('start')).order_by('start')
    years = sorted(list(set([start['start'].year for start in starts])), reverse = True)
    extra_context = {'years': years,'title':title}
    return render(request, template_name, extra_context)

@login_required
def json_ext_device_working_time(request, year):
    now = datetime.now()
    device_entries = DeviceEntry.objects.filter(internal_code__icontains="KCSK").order_by("id")
    timesheets = Timesheet.objects.filter(start__year=year,content_type__model='manufacturerecord')

    json = {}
    data = []
    total = device_entries.count()
    json['totalCount'] = total

    func = request.GET.get("func", None)
    page  = request.GET.get("page", None)
    limit = request.GET.get("limit", None)
    if func and func == '1':
        for de in device_entries:
            aaa = {'name': de.internal_code}
            mrs_id = [mr.id for mr in ManufactureRecord.objects.filter(device_entry=de)]
            ts = timesheets.filter(object_id__in=mrs_id)
            aaa['cNum'] = sum([t.difference_hours for t in ts],timedelta()).seconds
            data.append(aaa)
        response = HttpResponse(content=JSONEncoder().encode(data),
                    mimetype='text/javascript')
    elif func and func == '2':
        for de in device_entries:
            de_name = de.internal_code
            aaa = {0:de_name}
            mrs_id = [mr.id for mr in ManufactureRecord.objects.filter(device_entry=de)]
            ts = timesheets.filter(object_id__in=mrs_id)
            for i in range(12):
                if datetime(int(year),i+1,1) > now:
                    aaa[i+1] = 0
                else:
                    worked_hours = timedelta(0,0,0)
                    e_ts = ts.filter(start__month=i+1)
                    ts = ts.exclude(start__month=i+1)
                    worked_hours = sum([t.difference_hours for t in e_ts],timedelta())
                    aaa[i+1] = worked_hours.seconds
            data.append(aaa)
        response = HttpResponse(content=JSONEncoder().encode(data),
                    mimetype='text/javascript')
    else:
        if page and limit:
            paginator = Paginator(device_entries, int(limit))
            try:
                device_entries = paginator.page(int(page))
            except PageNotAnInteger:
                # If page is not an integer, deliver first page.
                device_entries = paginator.page(int(page))
            except EmptyPage:
                # If page is out of range (e.g. 9999), deliver last page of results.
                device_entries = paginator.page(paginator.num_pages)

        for de in device_entries:
            de_name = '<a href="'+reverse('ext_device_working_time_detail',args=[de.id])+'">'+ de.internal_code +'</>'
            aaa = {0:de_name}
            mrs_id = [mr.id for mr in ManufactureRecord.objects.filter(device_entry=de)]
            ts = timesheets.filter(object_id__in=mrs_id)
            for i in range(12):
                if datetime(int(year),i+1,1) > now:
                    aaa[i+1] = '-'
                else:
                    worked_hours = timedelta(0,0,0)
                    e_ts = ts.filter(start__month=i+1)
                    ts = ts.exclude(start__month=i+1)
                    worked_hours = sum([t.difference_hours for t in e_ts],timedelta())
                    aaa[i+1] = str(timedelta(seconds=worked_hours.seconds))
            data.append(aaa)
        json['data'] = data
        response = HttpResponse(content=JSONEncoder().encode(json),
                        mimetype='text/javascript')

    response['Content-Length'] = len(response.content)
    return response

@login_required
def ext_device_working_time_detail(request, device_entry_id, template_name="ext_device_working_time_detail.html"):
    device_entry = DeviceEntry.objects.get(id=device_entry_id)
    title = _("device_working_time_detail %s") % device_entry.internal_code
    extra_context = {'device_entry_id':device_entry_id,'title':title}
    return render(request, template_name, extra_context)

@login_required
def json_ext_device_working_time_detail(request, device_entry_id):
    device_entry = DeviceEntry.objects.get(id=device_entry_id)
    mrs_id = [mr.id for mr in ManufactureRecord.objects.filter(device_entry_id=device_entry_id)]
    timesheets = Timesheet.objects.filter(object_id__in=mrs_id,content_type__model='manufacturerecord')
    
    json = {}
    data = []
    total = timesheets.count()
    json['totalCount'] = total

    func = request.GET.get("func", None)
    page  = request.GET.get("page", None)
    limit = request.GET.get("limit", None)
    if func and func == '2':
        i_timesheets = timesheets
        for i in range(12):
            aaa = {'month': _("%d month") % (i+1)}
            ies_timesheets = timesheets.filter(start__month=i+1).order_by('-start')
            i_timesheets = i_timesheets.exclude(start__month=i+1).order_by('-start')
            worked_hours = sum([t.difference_hours for t in ies_timesheets],timedelta())
            aaa['cNum'] = worked_hours.seconds
            data.append(aaa)
        response = HttpResponse(content=JSONEncoder().encode(data),
                    mimetype='text/javascript')
    else:
        if page and limit:
            paginator = Paginator(timesheets, int(limit))
            try:
                timesheets = paginator.page(int(page))
            except PageNotAnInteger:
                # If page is not an integer, deliver first page.
                timesheets = paginator.page(int(page))
            except EmptyPage:
                # If page is out of range (e.g. 9999), deliver last page of results.
                timesheets = paginator.page(paginator.num_pages)

        for ts in timesheets:
            aaa = {'mi':ts.content_object.manufacture_item.__unicode__()}
            aaa['start'] = ts.start.strftime(DATETIMEFORMAT)
            aaa['end'] = ts.end.strftime(DATETIMEFORMAT)
            aaa['df'] = str(timedelta(seconds=ts.difference_hours.seconds))
            aaa['type'] = ts.get_type_display()
            data.append(aaa)

        json['data'] = data
        response = HttpResponse(content=JSONEncoder().encode(json),
                        mimetype='text/javascript')
    response['Content-Length'] = len(response.content)
    return response

@login_required
def ext_warehouse_inventory(request, template_name="ext_warehouse_inventory.html"):
    title = _("warehouse_inventory")
    list_category = 3#TODO
    tdrs = TransportDetailRecord.objects.filter(transport_list_detail__transport_list__list_category = list_category)
    starts = tdrs.values('created_at').annotate(Count('created_at')).order_by('created_at')
    years = sorted(list(set([start['created_at'].year for start in starts])), reverse = True)
    extra_context = {'years': years,'title':title}
    return render(request, template_name, extra_context)

@login_required
def json_ext_warehouse_inventory(request, year):
    list_category = 3#TODO
    now = datetime.now()
    tdrs = TransportDetailRecord.objects.filter(
        created_at__year = year,
        transport_list_detail__transport_list__list_category = list_category
    )
    items_id = list(set([tdr.inventory_item_entry.item.id for tdr in tdrs]))
    items = Item.objects.filter(id__in=items_id)
    
    json = {}
    data = []
    total = items.count()
    json['totalCount'] = total

    func = request.GET.get("func", None)
    page  = request.GET.get("page", None)
    limit = request.GET.get("limit", None)
    if page and limit:
        paginator = Paginator(items, int(limit))
        try:
            items = paginator.page(int(page))
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            items = paginator.page(int(page))
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            items = paginator.page(paginator.num_pages)

    if func and func == '2':

        for ie in items:
            aaa = {0: ie.id}
            ie_tdrs = tdrs.filter(inventory_item_entry__item=ie)
            for i in range(12):
                if datetime(int(year),i+1,1) > now:
                    aaa[i+1] = 0
                else:
                    i_ie_tdrs = ie_tdrs.filter(created_at__month=i+1).order_by('-created_at')
                    if i_ie_tdrs:
                        aaa[i+1] = i_ie_tdrs[0].inventory_qty
                    elif i!=0 and aaa[i]:
                        aaa[i+1] = aaa[i]
                    else:
                        aaa[i+1] = 0
            data.append(aaa)

        new_data = []
        for i in range(12):
            aaa = {'month': _("%d month") % (i+1)}
            count = 0
            for d in data:
                count += d[i+1]
            aaa['cNum'] = count
            new_data.append(aaa)
        response = HttpResponse(content=JSONEncoder().encode(new_data),
                    mimetype='text/javascript')
    else:
        for ie in items:
            aaa = {0:'<a href="'+reverse('ext_warehouse_inventory_detail',args=[ie.id])+'">'+ ie.code +'</>'}
            ie_tdrs = tdrs.filter(inventory_item_entry__item=ie)
            for i in range(12):
                if datetime(int(year),i+1,1) > now:
                    aaa[i+1] = '-'
                else:
                    i_ie_tdrs = ie_tdrs.filter(created_at__month=i+1).order_by('-created_at')
                    if i_ie_tdrs:
                        aaa[i+1] = str(i_ie_tdrs[0].inventory_qty)
                    elif i!=0 and aaa[i]:
                        aaa[i+1] = aaa[i]
                    else:
                        aaa[i+1] = '0'
            data.append(aaa)
        json['data'] = data
        response = HttpResponse(content=JSONEncoder().encode(json),
                    mimetype='text/javascript')

    response['Content-Length'] = len(response.content)
    return response

@login_required
def ext_warehouse_inventory_detail(request, item_id, template_name="ext_warehouse_inventory_detail.html"):
    item = Item.objects.get(id=item_id)
    title = _("warehouse_inventory_detail %s") % item.code
    extra_context = {'item_id':item_id,'title':title}
    return render(request, template_name, extra_context)

@login_required
def json_ext_warehouse_inventory_detail(request, item_id):
    item = Item.objects.get(id=item_id)
    list_category = 3#TODO
    tdrs = TransportDetailRecord.objects.filter(
        inventory_item_entry__item = item,
        transport_list_detail__transport_list__list_category = list_category
    ).order_by('-created_at')

    json = {}
    data = []
    total = tdrs.count()
    json['totalCount'] = total

    func = request.GET.get("func", None)
    page  = request.GET.get("page", None)
    limit = request.GET.get("limit", None)

    if func and func == '2':
        i_tdrs = tdrs
        for i in range(12):
            aaa = {'month': _("%d month") % (i+1)}
            ies_tdrs = i_tdrs.filter(created_at__month=i+1).order_by('-created_at')
            i_tdrs = i_tdrs.exclude(created_at__month=i+1).order_by('-created_at')
            aaa['cNum'] = ies_tdrs[0].inventory_qty if ies_tdrs else 0
            data.append(aaa)
        response = HttpResponse(content=JSONEncoder().encode(data),
                    mimetype='text/javascript')
    else:
        if page and limit:
            paginator = Paginator(tdrs, int(limit))
            try:
                tdrs = paginator.page(int(page))
            except PageNotAnInteger:
                # If page is not an integer, deliver first page.
                tdrs = paginator.page(int(page))
            except EmptyPage:
                # If page is out of range (e.g. 9999), deliver last page of results.
                tdrs = paginator.page(paginator.num_pages)

        for tdr in tdrs:
            aaa = {'c':tdr.created_at.strftime(DATETIMEFORMAT)}
            aaa['i'] = tdr.inventory_qty
            data.append(aaa)
        json['data'] = data
        response = HttpResponse(content=JSONEncoder().encode(json),
                        mimetype='text/javascript')
    response['Content-Length'] = len(response.content)
    return response

@login_required
def ext_knife_scraped(request, template_name="ext_knife_scraped.html"):
    title = _("knife_scraped")
    list_category = 3#kinfe
    transport_category = 3#Scrap
    tdrs = TransportDetailRecord.objects.filter(
        transport_list_detail__transport_list__list_category = list_category,
        transport_list_detail__transport_list__transport_category = transport_category
    )
    starts = tdrs.values('created_at').annotate(Count('created_at')).order_by('created_at')
    years = sorted(list(set([start['created_at'].year for start in starts])), reverse = True)
    extra_context = {'years': years,'title':title}
    return render(request, template_name, extra_context)

@login_required
def json_ext_knife_scraped(request, year):
    list_category = 3#kinfe
    transport_category = 3#Scrap
    now = datetime.now()
    tdrs = TransportDetailRecord.objects.filter(
        created_at__year = year,
        transport_list_detail__transport_list__list_category = list_category,
        transport_list_detail__transport_list__transport_category = transport_category
    )
    items_id = list(set([tdr.scrap_item_entry.item.id for tdr in tdrs if tdr.scrap_item_entry]))
    items = Item.objects.filter(id__in=items_id)
    
    json = {}
    data = []
    total = items.count()
    json['totalCount'] = total

    func = request.GET.get("func", None)
    page  = request.GET.get("page", None)
    limit = request.GET.get("limit", None)

    if func and func == '2':
        i_tdrs = tdrs
        for i in range(12):
            aaa = {'month': _("%d month") % (i+1)}
            ies_tdrs = i_tdrs.filter(created_at__month=i+1).order_by('-created_at')
            i_tdrs = i_tdrs.exclude(created_at__month=i+1).order_by('-created_at')
            count = 0
            for ie in items:
                ie_i_tdrs = ies_tdrs.filter(inventory_item_entry__item=ie)
                count += ie_i_tdrs[0].scrap_qty if ie_i_tdrs else 0
            aaa['cNum'] = count
            data.append(aaa)
        response = HttpResponse(content=JSONEncoder().encode(data),
                    mimetype='text/javascript')
    else:
        if page and limit:
            paginator = Paginator(items, int(limit))
            try:
                items = paginator.page(int(page))
            except PageNotAnInteger:
                # If page is not an integer, deliver first page.
                items = paginator.page(int(page))
            except EmptyPage:
                # If page is out of range (e.g. 9999), deliver last page of results.
                items = paginator.page(paginator.num_pages)

        for ie in items:
            aaa = {0:'<a href="'+reverse('ext_knife_scraped_detail',args=[ie.id])+'">'+ ie.code +'</>'}
            # aaa = {0:ie.code}
            ie_tdrs = tdrs.filter(inventory_item_entry__item=ie)
            for i in range(12):
                if datetime(int(year),i+1,1) > now:
                    aaa[i+1] = '-'
                else:
                    i_ie_tdrs = ie_tdrs.filter(created_at__month=i+1).order_by('-created_at')
                    if i_ie_tdrs:
                        aaa[i+1] = sum([t.scrap_qty for t in i_ie_tdrs])
                    elif i!=0 and aaa[i]:
                        aaa[i+1] = aaa[i]
                    else:
                        aaa[i+1] = '0'
            data.append(aaa)

        json['data'] = data
        response = HttpResponse(content=JSONEncoder().encode(json),
                        mimetype='text/javascript')
    response['Content-Length'] = len(response.content)
    return response

@login_required
def ext_knife_scraped_detail(request, item_id, template_name="ext_knife_scraped_detail.html"):
    item = Item.objects.get(id=item_id)
    title = _("ext_knife_scraped_detail %s") % item.code
    extra_context = {'item_id':item_id,'title':title}
    return render(request, template_name, extra_context)

@login_required
def json_ext_knife_scraped_detail(request, item_id):
    item = Item.objects.get(id=item_id)
    list_category = 3#TODO
    transport_category = 3#Scrap
    tdrs = TransportDetailRecord.objects.filter(
        inventory_item_entry__item = item,
        transport_list_detail__transport_list__list_category = list_category,
        transport_list_detail__transport_list__transport_category = transport_category
    ).order_by('-created_at')

    json = {}
    data = []
    total = tdrs.count()
    json['totalCount'] = total

    func = request.GET.get("func", None)
    page  = request.GET.get("page", None)
    limit = request.GET.get("limit", None)

    if func and func == '2':
        i_tdrs = tdrs
        for i in range(12):
            aaa = {'month': _("%d month") % (i+1)}
            ies_tdrs = i_tdrs.filter(created_at__month=i+1).order_by('-created_at')
            i_tdrs = i_tdrs.exclude(created_at__month=i+1).order_by('-created_at')
            aaa['cNum'] = ies_tdrs[0].scrap_qty if ies_tdrs else 0
            data.append(aaa)
        response = HttpResponse(content=JSONEncoder().encode(data),
                    mimetype='text/javascript')
    else:
        if page and limit:
            paginator = Paginator(tdrs, int(limit))
            try:
                tdrs = paginator.page(int(page))
            except PageNotAnInteger:
                # If page is not an integer, deliver first page.
                tdrs = paginator.page(int(page))
            except EmptyPage:
                # If page is out of range (e.g. 9999), deliver last page of results.
                tdrs = paginator.page(paginator.num_pages)

        for tdr in tdrs:
            aaa = {'c':tdr.created_at.strftime(DATETIMEFORMAT)}
            aaa['s'] = tdr.scrap_qty
            data.append(aaa)

        json['data'] = data
        response = HttpResponse(content=JSONEncoder().encode(json),
                        mimetype='text/javascript')
    response['Content-Length'] = len(response.content)
    return response






def generate_report_code(report_kind=None, pic_code=None, month=00):

    #机械加工工艺过程卡 ReportTechnology, agrument:pic_code
    if report_kind == 1:
        code = '000 04000 ' + pic_code + ' JGY'
        return code

    #产品生产质量控制记录表 ReportQuality, agrument:pic_code
    elif report_kind == 2:

        #统计流水号
        number = 0
        # report_quality_list = ReportQuality.objects.all()
        # for report in report_quality_list:
        #     if report.pic_code == pic_code:
        #         number += 1

        code = '000 04001 ' + pic_code + ' ' + '%02d' % (number + 1)
        return code

    #工序首件三检实测数据记录表 ReportOperationGroup, agrument:pic_code
    elif report_kind == 3:

        #统计流水号
        number = 0
        # report_operation_list = ReportFirstItem.objects.all()
        # for report in report_operation_list:
        #     if report.pic_code == pic_code:
        #         number += 1

        code = '000 04002 ' + pic_code + ' ' + '%02d' % (number + 1)
        return code

    #质量记录表（不合格处理单） ReportFail, agrument:pic_code
    elif report_kind == 4:

        #统计流水号
        number = 0
        # report_reject_list = ReportReject.objects.all()
        # for report in report_reject_list:
        #     if report.pic_code == pic_code:
        #         number += 1

        code = '000 06000 ' + pic_code + ' ' + '%02d' % (number + 1)
        return code

    #生产通知单（计划单） ReportPlan, agrument:month
    elif report_kind == 5:

        #统计流水号
        number = config.FLOW_NUMBER
        # report_plan_list = ReportPlan.objects.all()
        # for report in report_plan_list:
        #     if report.month == month:
        #         number += 1

        code = ('000 03000 ' + '%02d' + ' ' + '%02d') % (month, number)
        config.FLOW_NUMBER += 1
        return code
        
    else:
        print 'error'



def generate_first_item_report(request, productionline_id): #here is code orig
    redirecturl = request.REQUEST.get('next','')
    productionline = ProductionLine.objects.get(id=productionline_id)
    code = generate_report_code(3, productionline.code)
    
    return render(request, 'first_item_report.html', {
        'productionline':productionline,'code':code,
        'redirecturl':redirecturl,
        })


def generate_technology_report(request, technology_id):

    technology = Technology.objects.get(id=technology_id)
    operation_group_objects = technology.operation_groups.all()
    code = generate_report_code(1, technology.code)

    if TECHNOLOGY_REPORT_ROW != 0:
        row = TECHNOLOGY_REPORT_ROW
    else:
        row = 7

    operation_group_list = []
    for operation_record in operation_group_objects:
        operation_group_list.append(operation_record)

    total_table = []
    three_table = []
    list_length = len(operation_group_list)
    table_count = 0
    for i in xrange(0, list_length, row*3):                   #21

        try:
            table1_list = operation_group_list[i:i+row]      #7
            three_table.append(table1_list)
            table2_list = operation_group_list[i+row:i+row*2]   #7 14
            three_table.append(table2_list)
            table3_list = operation_group_list[i+row*2:i+row*3]  #14 21
            three_table.append(table3_list)
            total_table.append(three_table)
            three_table = []
        except:
            pass
            
    for table in total_table:
        for sub_table in table:
            while len(sub_table) < row:
                sub_table.append(' ')

    return render(request, 'technology_report.html', {
        'total_table':total_table,'code':code,
        'technology':technology,
        'operation_group_objects':operation_group_objects,
    })

def generate_technology_subpicture(request, operation_group_id):
    from technologies.models import OperationGroup
    operation_group = OperationGroup.objects.get(id=operation_group_id)
    redirecturl = request.REQUEST.get('next',None)
    return render(request, 'technology_subpicture.html', {
        'operation_group':operation_group,'UPLOAD_ROOT':UPLOAD_ROOT,
        'redirecturl':redirecturl,
    })


import re
from PIL import Image, ImageFont, ImageDraw
import base64
import StringIO
import os.path

def convert_special_character(string):

    target = r'\[(.*?)\]'
    special_characters = re.findall(target, string)

    modified_string = string

    for character in special_characters:

        #orig_character is used for replace
        orig_character = '[' + character + ']'

        #This is to handle [a, b, c]  [a,b,c] [a, b,c] and so on
        character_value_buff = ''.join(character.split(' '))
        character_value = character_value_buff.split(',')


        #model 1 [123, +0.001, -0.002, 12]
        if ('+' in character) or ('-' in character):
            character_table = '''
                <table class="inlinetable" style="font-size: {bound_number_size}px ! important;">
                    <tr>
                        <td style="padding: 0px; font-size: {font_size}px;" rowspan="2" height="6">{base_number}</td>               
                        <td style="padding: 0px;" height="3">{upper_bound}</td>
                    </tr>
                    <tr>
                        <td style="padding: 0px;" height="3">{lower_bound}</td>
                    </tr>
                </table>
                '''.format(base_number=character_value[0], upper_bound=character_value[1], 
                    lower_bound=character_value[2], font_size=character_value[-1], bound_number_size=int(character_value[-1])/2)

            modified_string = modified_string.replace(orig_character ,character_table)

        #model 3 [r, 3.2]
        elif len(character_value) == 2:
            image_path = "static/images/symbols/%s.png" %(character_value[0])
            if os.path.isfile(image_path) == True:
                
                font = ImageFont.truetype("static/images/symbols/DejaVuSans.ttf",13)
                value = character_value[1]

                image = Image.open("static/images/symbols/%s.png"% character_value[0])
                draw = ImageDraw.Draw(image)
                draw.text((0, 0), value, fill="black", font=font)
                del draw
                output = StringIO.StringIO()
                image.save(output, format="PNG")
                contents = output.getvalue()
                output.close()
                img_base64 = base64.b64encode(contents)



                character_table = '''
                    <table class="inlinetable" >
                        <tr>
                            <td style="padding: 0px;" height="3"><img src="data:image/jpeg;base64,{symbol}"></td>
                        </tr>               
                    </table>
                    '''.format(symbol=img_base64)

                modified_string = modified_string.replace(orig_character ,character_table)

        else:
            #model 3 [qty, 0.001, 0.002, 12]
            image_path = "static/images/symbols/%s.png" %(character_value[0])
            if os.path.isfile(image_path) == True:

                character_table = '''
                    <table class="table table-bordered inlinetable "  style="border: 1px solid #fff !important; font-size: {font_size}px !important">
                        <tr>
                            <td style="text-align:center; padding: 0px;"><img src="/site_media/images/symbols/{symbol}.png"></td>
                    '''.format(font_size=character_value[-1], symbol=character_value[0])

                for i in xrange(len(character_value) -2 ):
                    character_table += '<td style="text-align:center; padding: 0px">%s</td>' %(character_value[i+1])

                character_table += '</tr></table>'
                modified_string = modified_string.replace(orig_character ,character_table)

    return modified_string


def generate_plan_report(request, manufactureplan_id):

    manufactureplan = ManufacturePlan.objects.get(id=manufactureplan_id)
    order = manufactureplan.order
    product_item_list = order.product_items.all()
    code = generate_report_code(5, manufactureplan.code, 12)
    return render(request, 'plan_report.html', {
        'product_item_list':product_item_list,
        'code':code,
        })


def generate_quality_report(request, productionline_id):
    productionline = ProductionLine.objects.get(id=productionline_id)
    code = generate_report_code(2, productionline.code)

    return render(request, 'quality_report.html', {
        'productionline':productionline,'code':code,
    })

def generate_reject_project_report(request, productionline_id):
    reject_product_records = []
    productionline = ProductionLine.objects.get(id=productionline_id)
    for productionline in productionline.children_productionlines:
        reject_product_records.extend(productionline.reject_product_records.all())
    code = generate_report_code(4, productionline.code)
    return render(request, 'reject_project_report.html', {
        'code':code,'productionline':productionline,
        'reject_product_records':reject_product_records,
    })

def generate_single_reject_project_report(request, manufacture_item_id):
    manufacture_item = ManufactureItem.objects.get(id=manufacture_item_id)
    reject_product_records = manufacture_item.reject_product_records
    code = ''
    return render(request, 'reject_project_report.html', {
        'reject_product_records':reject_product_records,'code':code,
    })

