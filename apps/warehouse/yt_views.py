#-*- coding:utf-8 -*-
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from models import *
import datetime


##################################
#by xxd
##################################
from django.http import HttpResponseRedirect, HttpResponse
import json
import random
from manufactureplan.models import ProductionLine, ManufacturePlan, ManufactureItemGroup
from notification.models import Notice

def ajax_get_notice_data(request):
    # from notification.context_processors.notification
    result = 1
    msg = ""
    notice_unseen_count = 0
    if request.user.is_authenticated():
        result = 0
        now = datetime.datetime.now()
        notices = Notice.objects.filter(recipient=request.user,unseen=True)
        notice = notices[0] if notices else None
        if notice and (now - notice.added).seconds < 30:
            msg += notice.message
            notice_unseen_count = Notice.objects.unseen_count_for(request.user, on_site=True)
        #else:
        #    result = 1
        data = {'result':result,'msg':msg,'notice_unseen_count':notice_unseen_count}
    else:
        data = {'result':1,'msg':'You need to log in first.','notice_unseen_count':0}
    return HttpResponse('yuankong(' + json.dumps(data) + ');', content_type="application/json")

@login_required
def applications_list(request):
    # applications_list = Application.objects.all()
    manufactureplans_list = [m for m in ManufacturePlan.objects.all() if m.technology_ok and m.manufactureplan_workflow_status==2]
    manufactureplans_list.sort(key=lambda k: (k.start_time, k.is_item_entries_ready), reverse=True)
    return render_to_response('applications_list.html', {
        # 'applications_list':applications_list,
        'manufactureplans_list':manufactureplans_list,
        'l_m_storage_active':"active",
    }, context_instance=RequestContext(request))

@login_required
def ajax_set_manu_item_group_item_entries_ready(request):
    result = 0
    manu_item_group_id = int(request.POST['manu_item_group_id'])
    manu_item_group = ManufactureItemGroup.objects.get(id=manu_item_group_id)
    manu_item_group.is_item_entries_ready = True
    manu_item_group.save()
    #TODO message
    data = {'result':result,'msg':"msg"}
    return HttpResponse('yuankong(' + json.dumps(data) + ');', content_type="application/json")

msg = {
    0:'success',
    1:'没有需要分配的东西',
    2:'需要分配的东西不足',
    3:'分配错误',
    11: _("out of storage"),
}

# inventory = ItemJournal.objects.get(id=1)
# movement = ItemJournal.objects.get(id=2)
# import_item = ItemJournal.objects.get(id=3)

# warehouse = Location.objects.get(id=1)
# factory = Location.objects.get(id=2)

##################################
#apply_item_entries, by xxd
##################################
@login_required
def ajax_productionline_apply_item_entries(request):
    result = 0
    dom_content = ''

    productionline_id = int(request.POST.get('productionline_id'))
    productionline = ProductionLine.objects.get(id=int(productionline_id))
    item_entry_type = int(request.POST.get('item_entry_type'))
    # the type meaning, sea warehouse.models.CHOICE_LIST_CATEGORY
    if item_entry_type == 2:#Device, not use
        result = productionline_apply_devices(request,productionline)
    if item_entry_type == 3:#Knife
        result = productionline_apply_knifes(3,request,productionline)
    if item_entry_type == 4:#Tool, 与Knife用同一个函数
        result = productionline_apply_knifes(4,request,productionline)
    if item_entry_type == 5:#Material, not use
        result = productionline_apply_materials(request,productionline)

    if result == 0:
        dom_content = "正在申请中"
    data = {'result':result,'msg':msg[result],'dom_content':dom_content}
    return HttpResponse('yuankong(' + json.dumps(data) + ');', content_type="application/json")


##################################
#apply single item_entry, by xxd
##################################
@login_required
def productionline_apply_devices(request,productionline):
    result = 0
    empty_tag = True

    transport_list = None
    #create_transport_detail
    for oper_group_record in productionline.oper_group_records.all():
        #fing OperationGroup device
        device = oper_group_record.operation_group.device
        if device:
            empty_tag = False
            #create TransportList
            if transport_list == None:
                transport_list = create_transport_list(2,1,request.user,productionline)
            #find device_entries
            device_type = ContentType.objects.get_for_model(device)
            device_item = Item.objects.get(
                content_type_id = device_type.id,
                object_id = device.id,
            )
            result = create_transport_detail(request.user,transport_list,device_item,oper_group_record)

    if empty_tag == True:
        result = 1#没有需要分配的东西

    return result


@login_required
def productionline_apply_knifes(type,request,productionline):
    result = 0
    empty_tag = True

    transport_list = None
    #create_transport_detail
    for oper_group_record in productionline.oper_group_records.all():
        for operation_record in oper_group_record.operation_records.all():
            #fing Operation knifes or tools
            knifes_or_tools = []
            if type == 3:
                knifes_or_tools = operation_record.operation.knifes.all()
            elif type == 4:
                knifes_or_tools = operation_record.operation.tools.all()

            if knifes_or_tools:
                empty_tag = False
                if transport_list == None:
                    #create TransportList
                    transport_list = create_transport_list(type,1,request.user,productionline)

            for knife_or_tool in knifes_or_tools:
                #find device_items
                device_type = ContentType.objects.get_for_model(knife_or_tool)
                device_item = Item.objects.get(
                    content_type_id = device_type.id,
                    object_id = knife_or_tool.id,
                )
                #create_transport_detail
                result = create_transport_detail(request.user,transport_list,device_item,operation_record)

    if empty_tag == True:
        result = 1#没有需要分配的东西

    return result

#由productionline_apply_knifes()替代
@login_required
def productionline_apply_tools(request,productionline):
    result = 0
    return result

#由manufactureplan.views.productionline_apply_materials()替代
@login_required
def productionline_apply_materials(request,productionline):
    result = 0
    return result


##################################
#utils, by xxd
##################################
#create Transport
def create_transport_list(list_category,transport_category,user,productionline):
    transport_list = TransportList(
        list_category = list_category,
        transport_category = transport_category,
        updated_by = user,
        productionline = productionline
    )
    transport_list.save()
    return transport_list

#create TransportListDetail
def create_transport_detail(user,transport_list,device_item,content_object):
    result = 0
    transport_detail = TransportListDetail(
        transport_list = transport_list,
        item = device_item,
        unit = '个',
        updated_by = user,
        content_object = content_object
    )
    transport_detail.save()
    return result



@login_required
def transportlists_list(request, list_category_number, transport_category): #transport_category=3
    from warehouse.models import CHOICE_LIST_CATEGORY, CHOICE_TRANSPORT_CATEGORY
    transportlists = TransportList.objects.all().order_by('state','-updated_at')
    choice_list_category = []
    for LIST_CATEGORY in CHOICE_LIST_CATEGORY:
        list_category = list(LIST_CATEGORY)
        list_category.append(transportlists.filter(list_category=LIST_CATEGORY[0], transport_category=transport_category))
        list_category.append(CHOICE_TRANSPORT_CATEGORY)
        LIST_CATEGORY = tuple(list_category)
        choice_list_category.append(LIST_CATEGORY)
    CHOICE_LIST_CATEGORY = tuple(choice_list_category)
    

    return render_to_response('transportlists_list.html', {
        'CHOICE_LIST_CATEGORY': CHOICE_LIST_CATEGORY,
        'list_category_number': int(list_category_number),
        'transport_category': int(transport_category),
        'l_m_storage_active':"active",
    }, context_instance=RequestContext(request))

@login_required
def ajax_create_transportlist_verification(request):
    inventory   = ItemJournal.objects.get(id=1)
    result = 0
    msg = ''
    if request.method == 'POST':
        internal_code       = request.POST.get('internal_code', False)
        if not internal_code:
            result = 1
            msg = "请输入正确的出\入库单号。"
        elif TransportList.objects.filter(internal_code=str(internal_code)):
            result = 1
            msg = "出\入库单号已存在，请重新输入。"

        applicat_username   = request.POST.get('applicat', False)
        transport_category  = int(request.POST.get('transport_category', False))
        item_values         = request.POST.get('item_values', False)
        item_values_list    = json.loads(item_values) if item_values else []
        try:
            applicat = User.objects.get(username=applicat_username)
        except:
            result = 1
            msg = "请输入正确用户名。"
        for item_value in item_values_list:
            if not item_value.has_key("item_id") or not item_value['item_id']:
                result = 1
                msg = "请选择物品"
                break
            if not item_value.has_key("location_id") or not item_value['location_id']:
                result = 1
                msg = "请选择仓库"
                break

            item_id     = int(item_value['item_id'])
            item_note   = item_value['note_val']
            item        = Item.objects.get(id=item_id)
            location_id = int(item_value['location_id'])
            location    = Location.objects.get(id=location_id)
            try:
                item_qty    = float(item_value['qty_val'])
                if transport_category in [1,3,4]:
                    itementries = item.item_entries.filter(journal_id=1,location=location)
                    if itementries and item_qty > itementries[0].qty:
                        result = 1
                        msg = "数量大于库存，请先补充库存。"
                        break
                elif transport_category in [5] and item_qty > item.factory_itementry.qty:
                    result = 1
                    msg = "车间没有这么多数量，请先补充。"
                    break
            except:
                result = 1
                msg = "请输入正确的数量。"
                break

    data = {'result':result,'msg':msg}
    return HttpResponse('yuankong(' + json.dumps(data) + ');', content_type="application/json")

#filter items
def filter_items(items,transport_category):
    selectValues = None
    inventory   = ItemJournal.objects.get(id=1)
    if int(transport_category) in [1,3,4]:#output, Scrap, Borrow
        items2 = []
        item_locations = {}
        for item in items:
            item_entries = item.item_entries.filter(journal=inventory,location__type=1)
            if item_entries.count():
                items2.append(item)
            item_location = {}
            for item_entry in item_entries:
                item_location[item_entry.location.id] = "%s ( %d )" % (item_entry.location.__unicode__(), item_entry.qty)
            if item_location:
                item_locations[item.id] = item_location
        selectValues = json.dumps(item_locations)
        items = items2
    elif int(transport_category) in [5]:#Return
        items = [item for item in items if item.item_entries.filter(journal=inventory,location__type=2).count() in [1]]
    if not selectValues:
        selectValues = json.dumps({})
    return items, selectValues

@login_required
def create_transportlist(request, list_category, transport_category):
    from warehouse.models import CHOICE_LIST_CATEGORY, CHOICE_TRANSPORT_CATEGORY
    locations = Location.objects.filter(type=1)
    redirecturl = request.REQUEST.get('next','')
    LIST_CATEGORY       = CHOICE_LIST_CATEGORY[int(list_category)-1]
    TRANSPORT_CATEGORY  = CHOICE_TRANSPORT_CATEGORY[int(transport_category)-1]

    #sort items
    if int(list_category) == 1:
        items = Item.objects.filter(content_type__model='product')
    elif int(list_category) == 2:
        items = Item.objects.filter(content_type__model='device')
    elif int(list_category) == 3:
        items = Item.objects.filter(content_type__model='no_knife')
    elif int(list_category) == 4:
        items = Item.objects.filter(content_type__model='tool')
    elif int(list_category) == 5:
        items = Item.objects.filter(content_type__model='material')

    #filter items
    items, selectValues = filter_items(items,transport_category)

    if request.method == 'POST':
        internal_code       = request.POST.get('internal_code', False)
        applicat_username   = request.POST.get('applicat', False)
        item_values         = request.POST.get('item_values', False)
        item_values_list    = json.loads(item_values) if item_values else []
        applicat            = User.objects.get(username=applicat_username)
        #create transport_list

        transport_list = TransportList.objects.create(
            internal_code       = internal_code,
            list_category       = list_category,
            transport_category  = transport_category,
            applicat            = applicat,
            updated_by          = request.user
        )
        for item_value in item_values_list:
            item_id     = int(item_value['item_id'])
            item_qty    = float(item_value['qty_val'])
            item_note   = item_value['note_val']
            item        = Item.objects.get(id=item_id)
            location_id = int(item_value['location_id'])
            location    = Location.objects.get(id=location_id)
            transport_detail = TransportListDetail.objects.create(
                transport_list  = transport_list,
                item            = item,
                qty             = item_qty,
                unit            = '个',
                location        = location,
                note            = item_note,
                updated_by      = request.user
            )

        data = {'result':0,'msg':'msg'}
        return HttpResponse('yuankong(' + json.dumps(data) + ');', content_type="application/json")

    return render_to_response('create_transportlist.html', {
        'redirecturl':redirecturl,'items':items,'locations':locations,
        'list_category':list_category,'transport_category':transport_category,
        'LIST_CATEGORY':LIST_CATEGORY,'TRANSPORT_CATEGORY':TRANSPORT_CATEGORY,
        'selectValues':selectValues,
        'l_m_storage_active':"active",
    }, context_instance=RequestContext(request))


@login_required
def ajax_do_transport_verification(request):
    result = 0
    msg = ''
    if request.method == 'POST':
        transport_list_id   = int(request.POST.get('transport_list_id', False))
        transport_list = TransportList.objects.get(id=transport_list_id)
        inventory      = ItemJournal.objects.get(id=1)
        warehouse      = Location.objects.get(id=1)
        factory        = Location.objects.get(id=2)
        if transport_list.transport_category in [1,3,4]:
            location = warehouse
        elif transport_list.transport_category in [5]:
            location = factory
        if transport_list.transport_category in [1,3,4,5]:
            for transport_list_detail in transport_list.transport_list_details.all():
                itementries = ItemEntry.objects.filter(
                    journal  = inventory,
                    location = transport_list_detail.location,
                    item     = transport_list_detail.item
                )
                itementry = itementries[0] if itementries else None
                if not itementry or itementry.qty < transport_list_detail.qty:
                    result = 1
                    msg = "数量大于库存，请先补充库存。"

    data = {'result':result,'msg':msg}
    return HttpResponse('yuankong(' + json.dumps(data) + ');', content_type="application/json")


@login_required
def ajax_do_transport(request):
    redirecturl = request.REQUEST.get('next','')
    if request.method == 'POST':
        transport_list = TransportList.objects.get(id=int(request.POST.get('transport_list_id', False)))
        if transport_list.state == 1:
            #set correct function to get inventory item_entry
            fun_get_from_item_entry = None
            fun_get_to_item_entry = None
            if transport_list.list_category in [1,5]:
                fun_get_from_item_entry = get_from_item_entry
                fun_get_to_item_entry   = get_to_item_entry
            elif transport_list.list_category in [2,3,4]:
                fun_get_from_item_entry = get_from_device_entry
                fun_get_to_item_entry   = get_to_device_entry

            for transport_list_detail in transport_list.transport_list_details.all():
                #get inventory item_entry
                from_item_entry = fun_get_from_item_entry(request.user,transport_list_detail)
                to_item_entry   = fun_get_to_item_entry(request.user,transport_list_detail)
                #set inventory item_entry qty
                #Output
                if transport_list.transport_category in [1]:
                    from_item_entry.qty -= transport_list_detail.qty
                #Input
                elif transport_list.transport_category in [2]:
                    to_item_entry.qty   += transport_list_detail.qty
                #Scrap
                elif transport_list.transport_category in [3,4,5]:
                    from_item_entry.qty -= transport_list_detail.qty
                    to_item_entry.qty   += transport_list_detail.qty
                from_item_entry.save()
                to_item_entry.save()
                
                
                # Output
                if transport_list.transport_category in [1, 4]:
                    from_inventory_qty = 0
                    item = from_item_entry.item
                    same_location_type_item_entry = ItemEntry.objects.filter(item_id = item.id, location__type=1)
                    for item_entry in same_location_type_item_entry:
                        from_inventory_qty += item_entry.qty
                    #set productionline.location_status
                    productionline = transport_list.productionline
                    if productionline:
                        productionline.location_status = 1
                        productionline.save()

                    to_inventory_qty = to_item_entry.qty

                #Input
                elif transport_list.transport_category in [2, 5]:
                    to_inventory_qty = 0
                    item = to_item_entry.item
                    same_location_type_item_entry = ItemEntry.objects.filter(item_id = item.id, location__type=1)
                    for item_entry in same_location_type_item_entry:
                        to_inventory_qty += item_entry.qty
                    #set productionline.location_status
                    productionline = transport_list.productionline
                    if productionline:
                        productionline.location_status = 3
                        productionline.save()

                    from_inventory_qty = from_item_entry.qty
                    

                #Scrap
                elif transport_list.transport_category in [3]:
                    from_inventory_qty = 0
                    item = from_item_entry.item
                    same_location_type_item_entry = ItemEntry.objects.filter(item_id = item.id, location__type=1)
                    for item_entry in same_location_type_item_entry:
                        from_inventory_qty += item_entry.qty

                    to_inventory_qty = to_item_entry.qty
                    
                #create movement
                movement_entry = create_movement_entry(request.user,transport_list_detail, 
                                                        from_item_entry, to_item_entry,
                                                        from_inventory_qty, to_inventory_qty)

            #set transport_list state is Already done
            transport_list.state = transport_list.transport_category + 1
            transport_list.save()
        
    data = {'result':0,'msg':'msg'}
    return HttpResponse('yuankong(' + json.dumps(data) + ');', content_type="application/json")

def get_from_item_entry(user,transport_list_detail):
    inventory = ItemJournal.objects.get(id=1)
    #Output
    if transport_list_detail.transport_list.transport_category == 1:
        location = transport_list_detail.location
    #Input
    elif transport_list_detail.transport_list.transport_category == 2:
        location = Location.objects.get(id=2)#factory
    #Scrap
    elif transport_list_detail.transport_list.transport_category == 3:
        location = transport_list_detail.location
    #Borrow
    elif transport_list_detail.transport_list.transport_category == 4:
        location = transport_list_detail.location
    #Return
    elif transport_list_detail.transport_list.transport_category == 5:
        location = Location.objects.get(id=2)#factory

    item_entries = ItemEntry.objects.filter(
        journal  = inventory,
        location = location,
        item     = transport_list_detail.item
    )
    if item_entries:
        item_entry = item_entries[0]
    else:
        item_entry = ItemEntry.objects.create(
            journal     = inventory,
            location    = location,
            updated_by  = user,
            item        = transport_list_detail.item
        )
    return item_entry

def get_to_item_entry(user,transport_list_detail):
    inventory = ItemJournal.objects.get(id=1)
    #Output
    if transport_list_detail.transport_list.transport_category == 1:
        location = Location.objects.get(id=2)#factory
    #Input
    elif transport_list_detail.transport_list.transport_category == 2:
        location = transport_list_detail.location
    #Scrap
    elif transport_list_detail.transport_list.transport_category == 3:
        location = Location.objects.get(id=3)#Scrap
    #Borrow
    elif transport_list_detail.transport_list.transport_category == 4:
        location = Location.objects.get(id=2)#factory
    #Return
    elif transport_list_detail.transport_list.transport_category == 5:
        location = transport_list_detail.location

    item_entries = ItemEntry.objects.filter(
        journal  = inventory,
        location = location,
        item     = transport_list_detail.item
    )
    if item_entries:
        item_entry = item_entries[0]
    else:
        item_entry = ItemEntry.objects.create(
            journal     = inventory,
            location    = location,
            updated_by  = user,
            item        = transport_list_detail.item
        )
    return item_entry

def get_from_device_entry(user,transport_list_detail):
    inventory = ItemJournal.objects.get(id=1)
    #Output
    if transport_list_detail.transport_list.transport_category == 1:
        location = transport_list_detail.location
    #Input
    elif transport_list_detail.transport_list.transport_category == 2:
        location = Location.objects.get(id=2)#factory
    #Scrap
    elif transport_list_detail.transport_list.transport_category == 3:
        location = transport_list_detail.location
    #Borrow
    elif transport_list_detail.transport_list.transport_category == 4:
        location = transport_list_detail.location
    #Return
    elif transport_list_detail.transport_list.transport_category == 5:
        location = Location.objects.get(id=2)#factory

    device_entries = DeviceEntry.objects.filter(
        journal  = inventory,
        location = location,
        item     = transport_list_detail.item
    )
    if device_entries:
        device_entry = device_entries[0]
    else:
        device_entry = DeviceEntry.objects.create(
            journal     = inventory,
            location    = location,
            updated_by  = user,
            item        = transport_list_detail.item
        )
    return device_entry

def get_to_device_entry(user,transport_list_detail):
    inventory = ItemJournal.objects.get(id=1)
    #Output
    if transport_list_detail.transport_list.transport_category == 1:
        location = Location.objects.get(id=2)#factory
    #Input
    elif transport_list_detail.transport_list.transport_category == 2:
        location = transport_list_detail.location
    #Scrap
    elif transport_list_detail.transport_list.transport_category == 3:
        location = Location.objects.get(id=3)#Scrap
    #Borrow
    elif transport_list_detail.transport_list.transport_category == 4:
        location = Location.objects.get(id=2)#factory
    #Return
    elif transport_list_detail.transport_list.transport_category == 5:
        location = transport_list_detail.location

    device_entries = DeviceEntry.objects.filter(
        journal  = inventory,
        location = location,
        item     = transport_list_detail.item
    )
    if device_entries:
        device_entry = device_entries[0]
    else:
        device_entry = DeviceEntry.objects.create(
            journal     = inventory,
            location    = location,
            updated_by  = user,
            item        = transport_list_detail.item
        )
    return device_entry

def create_movement_entry(user,transport_list_detail, 
                          from_item_entry, to_item_entry,
                          from_inventory_qty, to_inventory_qty):

    transport_category = transport_list_detail.transport_list.transport_category
    if transport_category in [1, 3, 4]:
        inventory_item_entry = from_item_entry
        inventory_qty = from_inventory_qty

    elif transport_category in [2, 5]:
        inventory_item_entry = to_item_entry
        inventory_qty = to_inventory_qty

    name = None
    category = None
    norm_code = None
    cad_code = None
    furnace_batch = None
    try:
        name                    = transport_list_detail.item.content_object.name
    except:
        pass

    try:
        category                = transport_list_detail.item.content_object.category
    except:
        pass

    try:
        norm_code               = transport_list_detail.item.content_object.norm_code
    except:
        pass

    try:
        cad_code                = transport_list_detail.item.content_object.cad_code
    except:
        pass

    try:
        furnace_batch           = transport_list_detail.item.item_entries.all()[0].furnace_batch
    except:
        pass


    transport_detail_record = TransportDetailRecord.objects.create(
        name                    = name,
        category                = category,
        norm_code               = norm_code,
        cad_code                = cad_code,
        furnace_batch           = furnace_batch,
        unit                    = transport_list_detail.unit,
        amount                  = transport_list_detail.qty,
        note                    = transport_list_detail.note,
        transport_list_detail   = transport_list_detail,
        transport_list_number   = transport_list_detail.transport_list.internal_code,
        from_item_entry         = from_item_entry,
        to_item_entry           = to_item_entry,
        from_inventory          = from_inventory_qty,
        to_inventory            = to_inventory_qty,
        inventory_item_entry    = inventory_item_entry,
        inventory_qty           = inventory_qty,
        )

    return transport_detail_record




# 出库
@login_required
def bom_list(request):

    bom_list = BomEntry.objects.filter(bom_category = 1)
    bom_productionline_list = []
    productionline_list = []

    for bom in bom_list:
        if bom.productionline and bom.productionline not in productionline_list:
            print bom
            productionline_list.append(bom.productionline)
            bom_productionline_list.append(bom) 

    return render_to_response('warehouse/bom_list.html', {
        'bom_productionline_list':bom_productionline_list,
        'l_m_storage_active':"active",
    }, context_instance=RequestContext(request))


@login_required
def bom_detail(request, productionline_id):
    redirecturl = request.REQUEST.get('next','')
    bom_entry_list = BomEntry.objects.filter(productionline_id = productionline_id)
    return render_to_response('warehouse/bom_detail.html', {
        'bom_entry_list':bom_entry_list,'redirecturl':redirecturl,
        'productionline_id':productionline_id,
        'l_m_storage_active':"active",
    }, context_instance=RequestContext(request))

#by xxd
@login_required
def bom_output(request, productionline_id):
    bom_entry_list = BomEntry.objects.filter(productionline_id = productionline_id, bom_category = 1)
    inventory      = ItemJournal.objects.get(id=1)
    movement       = ItemJournal.objects.get(id=2)
    factory        = Location.objects.get(id=2)

    for current_bom in bom_entry_list:
        item_entries = ItemEntry.objects.filter(item=current_bom.item,journal=inventory)
        if current_bom.state == 1 and current_bom.is_enough:
            #set inventory qty
            to_reduce_qty = current_bom.qty
            for item_entry in item_entries:
                if item_entry.qty >= to_reduce_qty:
                    item_entry.qty -= to_reduce_qty
                else:
                    to_reduce_qty -= item_entry.qty
                    item_entry.qty = 0
                item_entry.save()
            
            #create movement
            new_entry = ItemEntry.objects.create(
                journal=movement,
                item=current_bom.item,
                location= factory,
                qty=current_bom.qty,
                updated_by= request.user,
            )
            current_bom.state = 2
            current_bom.save()

    return redirect('/xadmin/warehouse/itementry/?_p_journal__id__exact=1')

@login_required
def bom_import(request, productionline_id):
    
    bom_entry_list = BomEntry.objects.filter(productionline_id = productionline_id, bom_category = 2)

    item_entry_list = ItemEntry.objects.all()
    inventory = ItemJournal.objects.get(id=1)

    inventory_item_list = []
    for item_entry in item_entry_list:
        if item_entry.journal == inventory:
            inventory_item_list.append(item_entry)

    for current_bom in bom_entry_list:
        if current_bom.state != 5:

            current_bom.state = 5
            current_bom.save()


            import_it = ItemJournal.objects.get(id=3)
            warehouse = Location.objects.get(id=1)
            user = User.objects.get(id=1)
            
            new_entry = ItemEntry.objects.create(
                journal=import_it,
                item=current_bom.item,
                location= warehouse,
                qty=current_bom.qty,
                updated_by= user,
                )


            # for inventory_item in inventory_item_list:
            #   if new_entry.item == inventory_item.item:
            #       inventory_item.qty += new_entry.qty
            #       inventory_item.save()
    
    return redirect('/xadmin/warehouse/itementry/?_p_journal__id__exact=1')



##################################
#modify, by xxd
##################################
################export,by lxy
@login_required
def export_list(request):
    export_lists = generate_transport_list(1)
    for export_list in export_lists:
        print export_list.list_category
    return render(request, 'export_list.html', {
        'export_lists':export_lists,
        'nav_menu': True,
        'l_m_storage_active':"active",
    })

@login_required
def export_detail(request,export_list_id):
    redirecturl = request.REQUEST.get('next','')
    transport_list = TransportList.objects.get(id=export_list_id)

    applied_items = transport_list.transport_list_details.all()

    return render(request, 'export_detail.html', {
        'transport_list':transport_list,'redirecturl':redirecturl,
        'applied_items': applied_items,
        'export_list_id': export_list_id,
        'l_m_storage_active':"active",
    })


@login_required
def ajax_auto_apply_item_entries(request):
    result = 0

    transport_list_id = int(request.POST['transport_list_id'])

    #applied_items = request.POST['items'].split(',')[:-1]
    #for ai in applied_items:
    #    TransportListDetail.objects.get(id=ai)
    tlds = TransportListDetail.objects.filter(transport_list__id = transport_list_id)

    for tld in tlds:
        #tld.item_entry_code='111'
        item_entries = ItemEntry.objects.filter(item_id=tld.item.id, location=1) #the items must in the warehouse

        if len(item_entries) > 0:
            if item_entries[0].qty >= tld.qty:
                #item_entries[0].qty -= tld.qty
                tld.item_entry_code = item_entries[0].internal_code
                #item_entries[0].save()
                tld.save()

            else:
                result = 11
                break

    data = {
            'result':result,
            'message':msg[result],
            #'dom_content':dom_content
            }

    return HttpResponse('yuankong(' + json.dumps(data) + ');', content_type="application/json")







@login_required
def export_to_warehouse(request, export_list_id):
    warehouse_export(request,export_list_id)

    return redirect('/xadmin/warehouse/itementry/?_p_journal__id__exact=2')

#################import
@login_required
def import_list(request):
    import_lists = generate_transport_list(2)
    #print import_lists

    return render(request, 'import_list.html', {
        'import_lists':import_lists,
        'l_m_storage_active':"active",
        })

@login_required
def import_detail(request,import_list_id):
    redirecturl = request.REQUEST.get('next','')
    transport_list_details = generate_transport_detail(import_list_id)
    import_list = TransportList.objects.get(id = import_list_id)
    return render(request, 'import_detail.html', {
        'transport_list_details':transport_list_details,
        'import_list_id':import_list_id,'redirecturl':redirecturl,
        'import_list':import_list,
        'l_m_storage_active':"active",
        })

@login_required
def import_to_warehouse(request, import_list_id):
    warehouse_import(request,import_list_id)

    return redirect('/xadmin/warehouse/itementry/?_p_journal__id__exact=1')


###############function
def generate_transport_list(transport_category):
    transport_lists = TransportList.objects.filter(transport_category=transport_category).order_by('-created_at')
    return transport_lists


@login_required
def generate_transport_detail(transport_list_id):
    transport_list = TransportList.objects.get(id=transport_list_id)
    transport_list_details = transport_list.transport_list_details.all()
    return transport_list_details

def warehouse_export(requset,transport_list_id):

    transport_list         = TransportList.objects.get(id=transport_list_id)
    transport_list_details = transport_list.transport_list_details.all()

    inventory   = ItemJournal.objects.get(id=1)
    movement    = ItemJournal.objects.get(id=2)
    import_item = ItemJournal.objects.get(id=3)

    warehouse   = Location.objects.get(id=1)
    factory     = Location.objects.get(id=2)
    user        = requset.user
    
    product     = 1
    device      = 2
    knife       = 3
    tool        = 4
    material    = 5

    if transport_list.list_category == product:
        for transport_list_detail in transport_list_details:
            #find DeviceEntry, set location = factory
            item_entries = ItemEntry.objects.filter(journal=inventory,internal_code=transport_list_detail.item_entry_code).order_by('-created_at')
            if item_entries and item_entries[0].location == warehouse:
                #set inventory
                item_entries[0].delete()
                #create movement ItemEntry
                new_import = ItemEntry.objects.create(
                    journal = movement,
                    internal_code = transport_list_detail.item_entry_code,
                    item = transport_list_detail.item,
                    location = factory,
                    qty = 1,
                    updated_by = user,
                )
                #set transport_list state
                transport_list.state = 2    #"Already output"
                transport_list.save()

    elif transport_list.list_category == device:
        for transport_list_detail in transport_list_details:
            #find DeviceEntry, set location = factory
            device_entry = DeviceEntry.objects.get(internal_code = transport_list_detail.internal_code)
            device_entry.location = factory
            device_entry.save()
            #create movement ItemEntry
            new_import = ItemEntry.objects.create(
                journal = movement,
                internal_code = transport_list_detail.internal_code,
                item = transport_list_detail.item,
                location = factory,
                qty = 1,
                updated_by = user,
            )
            #set oper_group_record device_items
            oper_group_record = transport_list_detail.content_object
            oper_group_record.device_items.add(device_entry)
            oper_group_record.save()
            #set transport_list state
            transport_list.state = 2    #"Already output"
            transport_list.save()

    elif transport_list.list_category == knife:
        for transport_list_detail in transport_list_details:
            #find DeviceEntry, set location = factory
            device_entry = DeviceEntry.objects.get(internal_code = transport_list_detail.item_entry_code)
            if device_entry.location == warehouse:
                device_entry.location = factory
                device_entry.qty = device_entry.qty - transport_list_detail.qty
                device_entry.save()
                #create movement ItemEntry
                new_import = ItemEntry.objects.create(
                    journal = movement,
                    internal_code = transport_list_detail.item_entry_code,
                    item = transport_list_detail.item,
                    location = factory,
                    qty = 1,
                    updated_by = user,
                )
                #set operation_record knife_items
                operation_record = transport_list_detail.content_object
                operation_record.knife_items.add(device_entry)
                operation_record.save()
                #set transport_list state
                transport_list.state = 2    #"Already output"
                transport_list.save()
            else:
                #set transport_list state
                transport_list.state = 3    #"Insufficient"
                transport_list.save()

    elif transport_list.list_category == tool:
        for transport_list_detail in transport_list_details:
            #find DeviceEntry, set location = factory
            device_entry = DeviceEntry.objects.get(internal_code = transport_list_detail.item_entry_code)
            if device_entry.location == warehouse:
                device_entry.location = factory
                device_entry.qty = device_entry.qty - transport_list_detail.qty
                device_entry.save()
                #create movement ItemEntry
                new_import = ItemEntry.objects.create(
                    journal = movement,
                    internal_code = transport_list_detail.item_entry_code,
                    item = transport_list_detail.item,
                    location = factory,
                    qty = 1,
                    updated_by = user,
                )
                #set operation_record knife_items
                operation_record = transport_list_detail.content_object
                operation_record.tool_items.add(device_entry)
                operation_record.save()
                #set transport_list state
                transport_list.state = 2    #"Already output"
                transport_list.save()
            else:
                #set transport_list state
                transport_list.state = 3    #"Insufficient"
                transport_list.save()

    elif transport_list.list_category == material:
        pass
    else:
        pass

    return 0

def warehouse_import(requset,transport_list_id):

    transport_list = TransportList.objects.get(id=transport_list_id)
    transport_list_details = transport_list.transport_list_details.all()

    inventory = ItemJournal.objects.get(id=1)
    movement = ItemJournal.objects.get(id=2)
    import_item = ItemJournal.objects.get(id=3)

    warehouse = Location.objects.get(id=1)
    factory = Location.objects.get(id=2)
    user = requset.user
    
    product  = 1
    device   = 2
    knife    = 3
    tool     = 4
    material = 5

    if transport_list.list_category == product:
        for transport_list_detail in transport_list_details:
            new_inventory = ItemEntry.objects.create(
                journal = inventory,
                internal_code = transport_list_detail.item_entry_code,
                item = transport_list_detail.item,
                location = warehouse,
                qty = 1,
                updated_by = user,
            )

            new_import = ItemEntry.objects.create(
                journal = import_item,
                internal_code = transport_list_detail.item_entry_code,
                item = transport_list_detail.item,
                location = warehouse,
                qty = 1,
                updated_by = user,
            )
        transport_list.state = 5
        transport_list.save()

    elif transport_list.list_category == device:
        for transport_list_detail in transport_list_details:
            new_inventory = DeviceEntry.objects.create(
                journal = inventory,
                internal_code = transport_list_detail.internal_code,
                item = transport_list_detail.item,
                location = warehouse,
                qty = 1,
                updated_by = user,
                usage_time = 0,
                )

            new_import = ItemEntry.objects.create(
                journal = import_item,
                internal_code = transport_list_detail.internal_code,
                item = transport_list_detail.item,
                location = warehouse,
                qty = 1,
                updated_by = user,
                )

    elif transport_list.list_category == knife:

        for transport_list_detail in transport_list_details:
            qty = transport_list_detail.qty

            knife_in_warehouse = DeviceEntry.objects.filter(internal_code__startswith=transport_list_detail.internal_code).count()
            
            for i in xrange(knife_in_warehouse+1, knife_in_warehouse+1+qty):
                new_deviceentry = DeviceEntry.objects.create(
                    journal       = inventory,
                    item          = transport_list_detail.item,
                    internal_code = transport_list_detail.internal_code + '%02d' % (i),
                    location      = warehouse,
                    qty           = 1,
                    updated_by    = user,
                    usage_time    = 0,
                    )


    elif transport_list.list_category == material or transport_list.list_category == tool:

        item_entry_list = ItemEntry.objects.all()
        inventory_items = []
        inventory_item_list = []

        for item_entry in item_entry_list:
            if item_entry.journal == inventory:
                inventory_item_list.append(item_entry)
                inventory_items.append(item_entry.item)


        for transport_list_detail in transport_list_details:

            transport_item = transport_list_detail.item
            transport_qty = transport_list_detail.qty

            #create a warehouse import record
            new_import = ItemEntry.objects.create(
                journal = import_item,
                item = transport_item,
                location = warehouse,
                qty = transport_qty,
                updated_by = user,
                )

            #add qty to a exist item
            if transport_item in inventory_items:
                for inventory_item in inventory_item_list:
                    if transport_item == inventory_item.item:                            
                        inventory_item.qty += transport_qty
                        inventory_item.save()

            else:
                #create a warehouse inventory record
                new_entry = ItemEntry.objects.create(
                    journal=inventory,
                    item=transport_item,
                    location= warehouse,
                    qty=transport_qty,
                    updated_by= user,
                    )
        
    else:
        pass

    return 0




from forms import TransferListForm
from models import TransferList
@login_required
def transfer_and_verify(request):
    if request.method == 'POST':
        form = TransferListForm(request.POST)
        if form.is_valid():

            transfer_form = form.save(commit=False)
            transfer_form.applicat = User.objects.get(username=form.cleaned_data['user'])
            transfer_form.save()
            form.save_m2m()

            return HttpResponseRedirect('#')
    else:
        form = TransferListForm()

    return render(request, 'transfer_and_verify.html', {
        'form': form,
    })



from django.db.models import Count
from device.models import Knife, KnifeAttribute

# by lxy
global_all_knifes = None
# #load global data
@login_required
def ajax_load_global_data(request):

    post_transport_category = request.POST['transport_category']
    global global_all_knifes
    # if not global_all_knifes:

    knife_contenttype = ContentType.objects.get_for_model(Knife)
    items = Item.objects.filter(content_type=knife_contenttype) #all knife in items
    transport_items, selectValues = filter_items(items, post_transport_category) #item of knifes about transport
    transport_item_ids = [item.object_id for item in transport_items]
    knife_to_filter = Knife.objects.filter(id__in = transport_item_ids)
    global_all_knifes = knife_to_filter

    data = {
        'selectValues':json.loads(selectValues)
    }

    return HttpResponse('yuankong(' + json.dumps(data) + ');', content_type="application/json")


#initial data about knife name
@login_required
def ajax_chained_selected_modal(request):

    kind_of_knife = Knife.objects.values('name').annotate(name_count=Count('name')).order_by('-name_count')

    data = {
        'kind_of_knife':list(kind_of_knife)
        }

    return HttpResponse('yuankong(' + json.dumps(data) + ');', content_type="application/json")

def sort_attribute_value(attributes):
    attribute_value_float = []
    attribute_only_value = []
    converted = []

    for value in attributes:
        converted_value = {'attribute_count': value['attribute_count'], 'value': float(value['value'])}
        attribute_value_float.append(converted_value)
        attribute_only_value.append(float(value['value']))

    attribute_only_value.sort()
    for i in attribute_only_value:
        for value in attribute_value_float:
            if i == value["value"]:
                converted.append(value)

    return converted

def filter_knifes(all_knifes, attributes_list):
    filted_knifes = all_knifes
    for attribute in attributes_list:
        if attribute[1] == "empty":
            attribute[1] = ''
        if attribute[1]:
            filted_knifes = filted_knifes.filter(knife_attributes__attribute_id=attribute[0], knife_attributes__value=attribute[1])
    return filted_knifes

@login_required
def ajax_knife_attribute_data(request):

    #selected option
    kind_of_knife = request.POST['kind_of_knife']
    post_caizhi = request.POST['caizhi']
    post_zhijing = request.POST['zhijing']
    post_D = request.POST['D']
    post_R_angle = request.POST['R_angle']
    post_total_length = request.POST['total_length']
    post_zhishengwei = request.POST['zhishengwei']    
    post_blade_length = request.POST['blade_length'] 
    post_blade_amount = request.POST['blade_amount'] 
    post_specification = request.POST['specification'].replace('\xc2\xa0', ' ')
    post_knife_selected = request.POST['knife_selected']

    knife_attribute = KnifeAttribute.objects.all()

    all_attributes          = knife_attribute.filter(knife__name=kind_of_knife)
    caizhi_attributes       = all_attributes.filter(attribute_id=5)
    zhijing_attributes      = all_attributes.filter(attribute_id=6)
    D_attributes            = all_attributes.filter(attribute_id=17)
    R_angle_attributes      = all_attributes.filter(attribute_id=7)
    total_length_attributes = all_attributes.filter(attribute_id=8)
    zhishengwei_attributes  = all_attributes.filter(attribute_id=18)
    blade_length_attributes = all_attributes.filter(attribute_id=9)
    blade_amount_attributes = all_attributes.filter(attribute_id=10)
    specification_attributes = all_attributes.filter(attribute_id=11)

    #group by attributes
    caizhi = caizhi_attributes.values('value').annotate(attribute_count=Count('attribute')).order_by('-attribute_count')
    zhijing = zhijing_attributes.values('value').annotate(attribute_count=Count('attribute')).order_by('value')
    D = D_attributes.values('value').annotate(attribute_count=Count('attribute')).order_by('value')
    R_angle = R_angle_attributes.values('value').annotate(attribute_count=Count('attribute')).order_by('value')
    total_length = total_length_attributes.values('value').annotate(attribute_count=Count('attribute')).order_by('value')
    zhishengwei = zhishengwei_attributes.values('value').annotate(attribute_count=Count('attribute')).order_by('value')
    blade_length = blade_length_attributes.values('value').annotate(attribute_count=Count('attribute')).order_by('value')
    blade_amount = blade_amount_attributes.values('value').annotate(attribute_count=Count('attribute')).order_by('value')
    specification = specification_attributes.values('value').annotate(attribute_count=Count('attribute')).order_by('value')

    # zhijing = sort_attribute_value(zhijing)
    # R_angle = sort_attribute_value(R_angle)
    # total_length = sort_attribute_value(total_length)
    # zhishengwei = sort_attribute_value(zhishengwei)
    # blade_length = sort_attribute_value(blade_length)
    # blade_amount = sort_attribute_value(blade_amount)

    attributes_list = [ [5, post_caizhi],
                        [6, post_zhijing],
                        [17, post_D],
                        [7, post_R_angle],
                        [8, post_total_length],
                        [18, post_zhishengwei],
                        [9, post_blade_length],
                        [10, post_blade_amount],
                        [11, post_specification]
                        ]


    knifes = ''
    knife_contenttype = ContentType.objects.get_for_model(Knife)
    for attribute in attributes_list:
        if attribute[1]:
            all_knifes = global_all_knifes.filter(name=kind_of_knife)  
            knifes = filter_knifes(all_knifes, attributes_list)
            break

    knifes_description = [[knife.id, str(knife)] for knife in knifes]

    item_selected = ['', '']
    item_selected_id = item_selected_str = None
    if post_knife_selected:
        knife_contenttype = ContentType.objects.get(app_label="device",model="knife")
        item = Item.objects.get(content_type=knife_contenttype, object_id=int(post_knife_selected))
        item_selected = [item.id, str(item)]
        item_selected_id = item.id
        item_selected_str = "%s" % item

    data = {

            'caizhi':list(caizhi),
            'zhijing':list(zhijing),
            'D': list(D),
            'R_angle': list(R_angle),
            'total_length': list(total_length),
            'zhishengwei' :list(zhishengwei),
            'blade_length' :list(blade_length),
            'blade_amount' :list(blade_amount),
            'specification':list(specification),

            'knifes_description':knifes_description,
            'item_selected':item_selected,
            'item_selected_id':item_selected_id,
            'item_selected_str':item_selected_str,

            }

    return HttpResponse('yuankong(' + json.dumps(data) + ');', content_type="application/json")
