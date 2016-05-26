from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.shortcuts import render, get_object_or_404
from django.utils.simplejson.encoder import JSONEncoder
from django.contrib.contenttypes.models import ContentType
from yt_file.models import File
from companydepartment.models import *
from companydepartment.forms import *


def compnay_files_list(request,company_id):
    company = get_object_or_404(Company,id = company_id)
    fileowner_type = ContentType.objects.get_for_model(company)
    
    return render_to_response('company/company_files.html', {
        'company':company,'contenttype_id':fileowner_type.id
    }, context_instance=RequestContext(request))
    
def department_files_list(request,department_id):
    department = get_object_or_404(Department,id = department_id)
    fileowner_type = ContentType.objects.get_for_model(department)
    
    return render_to_response('department/department_files.html', {
        'department':department,'contenttype_id':fileowner_type.id
    }, context_instance=RequestContext(request))


def dep_serializable_object(node):
    obj = {
        'id': node.id,
        'name': node.name,
        'description': node.description,
        'children': [dep_serializable_object(ch) for ch in node.get_children() if node.id != ch.id],
    }
    return obj

def comp_serializable_object(node):
    obj = {
        'id': node.id,
        'name': node.name,
        'description': node.description,
        'children': [comp_serializable_object(ch) for ch in node.get_children() if node.id != ch.id],
        'href': '/hr/dep/structure/'+str(node.id),
    }
    return obj

def json_departments_request(request, company_id):
    company = get_object_or_404(Company, id=company_id)
    c_depts = Department.objects.filter(belong_to=company).order_by('id')
        
    root_depts = [d for d in c_depts if d.parent_id == None]
    d_data = [dep_serializable_object(root_dept) for root_dept in root_depts]

    # test_data = [{"name": "w1","description": "e1","children": []},{"name": "w2","description": "e2","children": [{"name": "t2","description": "y2",'leaf': True}]},{"name": "w3","description": "e3","children": [{"name": "t3","description": "y3",'leaf': True}]},{"name": "w4","description": "e4","children": [{"name": "t4","description": "y4",'leaf': True}]},]
    
    # # test for lxy phonegap
    # import json
    # data = {'result':0,'msg':'error'}
    # return HttpResponse('yuankong(' + json.dumps(data) + ');', content_type="application/json")

    response = HttpResponse(content=JSONEncoder().encode(d_data),
                    mimetype='text/javascript')
    response['Content-Length'] = len(response.content)
    return response

def json_companys_request(request):
    companys = Company.objects.all().order_by('id')

    root_comps = [c for c in companys if c.parent_id == None]
    c_data = [comp_serializable_object(root_comp) for root_comp in root_comps]

    response = HttpResponse(content=JSONEncoder().encode(c_data),mimetype='text/javascript')
    response['Content-Length'] = len(response.content)
    return response


def departments_structure(request, company_id =1):
    companys = Company.objects.all().order_by('id')
    company = get_object_or_404(Company, id=company_id)
    return render_to_response('department/departments_structure.html', {
        'company_id': company_id,'company': company,'companys': companys
    }, context_instance=RequestContext(request))

def companys_structure(request):
    return render_to_response('company/companys_structure.html', {
    }, context_instance=RequestContext(request))

def departments_list(request, template_name="department/departments_list.html"):
    departments = Department.objects.all().order_by('id')
    return render_to_response(template_name, {
        'departments': departments,
    }, context_instance=RequestContext(request))

def department_add(request):
    if request.method == 'POST':  # If the form has been submitted...
        form = HRDepartmentAddForm(request.POST)  # A form bound to the POST data
        if form.is_valid():  # All validation rules pass
            try:
                bt = int(request.POST.get('belong_to'))
            except:
                bt = None
            try:
                pd = int(request.POST.get('parent'))
            except:
                pd = None
            c = Department(
                name=form.cleaned_data['name'],
                description=form.cleaned_data['description'],
                address=form.cleaned_data['address'],
                city=form.cleaned_data['city'],
                state=form.cleaned_data['state'],
                zip_code=form.cleaned_data['zip_code'],
                belong_to_id=bt,
                parent_id=pd
            )
            c.save()
            return HttpResponseRedirect('department/departments_list.html')
    else:
        form = HRDepartmentAddForm()  # An unbound form

    return render_to_response('department/department_add.html', {
        'form': form,
    }, context_instance=RequestContext(request))
    
def department_edit(request, department_id=None):
    instance = get_object_or_404(Department, id=department_id)
    if request.method == 'POST':  # If the form has been submitted...
        form = HRDepartmentAddModelForm(request.POST, instance=instance)  # A form bound to the POST data
        if form.is_valid():  # All validation rules pass
            instance = form.save(commit=False)
            instance.save()
            return HttpResponseRedirect('department/departments_list.html')
    else:
        form = HRDepartmentAddModelForm(instance=instance)  # An unbound form

    return render_to_response('department/department_edit.html', {
        'department_id': department_id,
        'form': form,
    }, context_instance=RequestContext(request))

def department_del(request):
    if request.method == 'POST':
        if request.POST['del_id']:
            del_id = int(request.POST['del_id'])
        instance = get_object_or_404(Department, id=del_id)
        departments = instance.children.all()
        for department in departments:
            department.parent_id = None
            department.save()
        instance.delete()
        return 0
    return render_to_response('department/departments_list.html', {
    }, context_instance=RequestContext(request))
    
def companys_list(request, template_name="company/companys_list.html"):
    companys = Company.objects.all().order_by('id')
    return render_to_response(template_name, {
        'companys': companys,
    }, context_instance=RequestContext(request))

def company_add(request):
    if request.method == 'POST':  # If the form has been submitted...
        form = HRCompanyAddModelForm(request.POST)  # A form bound to the POST data
        if form.is_valid():  # All validation rules pass
            try:
                pd = int(request.POST.get('parent'))
            except:
                pd = None
                
            
            c = Company(
                name=form.cleaned_data['name'],
                #name = (''.join([chr(ord(x) ^ 0x88) for x in name])).encode('hex'),
                description=form.cleaned_data['description'],
                address=form.cleaned_data['address'],
                city=form.cleaned_data['city'],
                state=form.cleaned_data['state'],
                zip_code=form.cleaned_data['zip_code'],
                parent_id=pd
            )
            c.save()
            return HttpResponseRedirect("company/companys_list.html")
    else:
        form = HRCompanyAddModelForm()  # An unbound form

    return render_to_response('company/company_add.html', {
        'form': form,
    }, context_instance=RequestContext(request))
    
def company_edit(request, company_id=None):
    instance = get_object_or_404(Company, id=company_id)
    if request.method == 'POST':  # If the form has been submitted...
        form = HRCompanyAddModelForm(request.POST, instance=instance)  # A form bound to the POST data
        if form.is_valid():  # All validation rules pass
            instance = form.save(commit=False)
            instance.save()
            return HttpResponseRedirect("company/companys_list.html")
    else:
        form = HRCompanyAddModelForm(instance=instance)  # An unbound form

    return render_to_response('company/company_edit.html', {
        'company_id': company_id,
        'form': form,
    }, context_instance=RequestContext(request))

def company_del(request):
    if request.method == 'POST':
        if request.POST['del_id']:
            del_id = int(request.POST['del_id'])
        instance = get_object_or_404(Company, id=del_id)
        companys = instance.children.all()
        for company in companys:
            company.parent_id = None
            company.save()
        instance.delete()
        return 0
    return HttpResponseRedirect("company/companys_list.html")
