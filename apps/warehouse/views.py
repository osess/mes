from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.shortcuts import redirect
from models import Item

def _render(template, payload, request):
    #payload['app_name']=Booking._meta.app_label
    #payload['tabs']=tabs(tab_name)
    #log.debug("paylod=%r" % payload)
    
    return render_to_response(template, payload, context_instance = RequestContext(request) )


def index(request):
    
    return _render('warehouse/index.html', {}, request)

def item_list(request):
    item_list = Item.objects.all()
    return _render('warehouse/item/list.html', {
            'item_list':item_list,
            'l_m_storage_active':"active",
        }, request)

def item_detail(request, item_code):
    from forms import ItemForm
    item = get_object_or_404(Item, code=item_code)
    if request.method=="POST":
        item_form = ItemForm(instance=item, data=request.POST)
        if item_form.is_valid():
            item = item_form.save()
            return redirect(item)
    else:
        item_form = ItemForm(instance=item)
    
    payload={
                'item':item,
                'item_form':item_form,
                'l_m_storage_active':"active",
             }
    return _render('warehouse/item/detail.html', payload, request)

    



