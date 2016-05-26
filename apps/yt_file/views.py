from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.shortcuts import render, get_object_or_404
from django.contrib.contenttypes.models import ContentType
from yt_file.models import *
from yt_file.forms import *
import base64
from yt_file import util

from extensions.custom_fields.encrypt import decode_notin_field
XOR_KEY = 0x88

def files_list(request):
    files = []
    if request.user.has_perm('file.open_file'):
        files = File.objects.all().order_by('content_type','-id')
    else:
        return HttpResponseRedirect(reverse('hr.views.page404'))
    
    return render_to_response('files_list.html', {
        'files': files,
    },context_instance=RequestContext(request))

def upload_file(request, contenttype_id, object_id):
    result = 0
    redirecturl = request.REQUEST.get('next','')
    contenttype = get_object_or_404(ContentType,id=contenttype_id)
    obj = contenttype.get_object_for_this_type(pk=object_id)

    file_content = ''
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES['file']
            display_name = request.POST['display_name'] if request.POST.get('display_name') else file.name
            path = request.POST['path'] if request.POST.get('path') else 'No path'

            result = util.yt_file_save(file, obj, display_name, path)
        if result == 0:
            if redirecturl.strip() != '':
                return HttpResponseRedirect(redirecturl)
            elif ContentType.objects.get_for_model(obj).model=='technology':
                return HttpResponseRedirect(reverse('admin:technologies_technology_changelist'))
            elif ContentType.objects.get_for_model(obj).model=='operationgroup':
                return HttpResponseRedirect(reverse('admin:technologies_operationgroup_changelist'))
            elif ContentType.objects.get_for_model(obj).model=='manufactureplan':
                return HttpResponseRedirect(reverse('admin:manufactureplan_manufactureplan_changelist'))
            else:
                return HttpResponseRedirect('/')
        else:
            raise forms.ValidationError('YT Error: something wrong in file upload. FIX......')
    else:
        form = UploadFileForm()
    
    if ContentType.objects.get_for_model(obj).model in ['technology', 'operationgroup', 'manufactureplan']:
        return render_to_response('upload_modal_content.html', {
            'form': form, 'contenttype_id':contenttype_id, 'object_id': object_id
        },context_instance=RequestContext(request))
    else:
        return render_to_response('upload.html', {
            'form': form,'file_content': file_content,'object_id': object_id,
            'contenttype_id':contenttype_id,'redirecturl':redirecturl
        },context_instance=RequestContext(request))
    
def uploadsuccess(request, file_id):
    file = File.objects.get(id=file_id)
    #permission judge
    #if not request.user.has_perm('file.open_file'):
    #    return HttpResponseRedirect(reverse('hr.views.page404'))
    
    file_data = ''
    content = ''
    file_name = file.name
    content = decode_notin_field(file.data)#to see custom_fields.encrypt
    if file.imgtag:
        file_data = "data:image/jpeg;base64,"+base64.b64encode(content)
    else:
        response = HttpResponse(mimetype='text/csv')
        response['Content-Disposition'] = 'attachment; filename=%s' % file_name.encode('utf-8')
        response.write(content)
        return response
    
    return render_to_response('upload_success.html', {
        'content': content,'file_data':file_data,'file_name':file_name,'imgtag': file.imgtag
    }, context_instance=RequestContext(request))

def download_directory_file(request, file_id):
    from django.utils.encoding import smart_str, smart_unicode
    file = FileDirectory.objects.get(id=file_id)
    content = file.data.read()
    response = HttpResponse(mimetype='text/csv')
    response['Content-Disposition'] = 'attachment; filename=%s' % smart_str("".join(file.name.split()))
    response.write(content)
    return response

def file_remove(request, file_id):
    if request.method == 'GET':
        file = get_object_or_404(File, id=file_id)
        if file.status == 1:
            file.status=0
            file.save()
        redirecturl = request.REQUEST.get('next','')
        return HttpResponseRedirect(redirecturl)
    return HttpResponseRedirect('404.html')

def file_delete(request, file_id):
    if request.method == 'GET':
        file = get_object_or_404(File, id=file_id)
        file.delete()
        redirecturl = request.REQUEST.get('next','')
        return HttpResponseRedirect(redirecturl)
    return HttpResponseRedirect('404.html')

def file_edit(request, file_id):
    pass

def view_files(request, contenttype_id, obj_id):
    
    files = File.objects.filter(content_type_id = contenttype_id, object_id = object_id)
    
    #permission judge
    #if not request.user.has_perm('file.open_file'):
    #    return HttpResponseRedirect(reverse('hr.views.page404'))
    if len(files) == 1:
        file = files[0]
        file_data = ''
        content = ''
        file_name = file.name
        content = decode_notin_field(file.data)#to see custom_fields.encrypt
        if file.imgtag:
            file_data = "data:image/jpeg;base64,"+base64.b64encode(content)
        else:
            response = HttpResponse(mimetype='text/csv')
            response['Content-Disposition'] = 'attachment; filename=%s' % file_name.encode('utf-8')
            response.write(content)
            return response
    else:
        pass
    
    return render_to_response('upload_success.html', {
        'content': content,
        'file_data':file_data,
        'file_name':file_name,
        'imgtag': file.imgtag
    }, context_instance=RequestContext(request))

# def download_directory_files(request, file_id):
#     from django.utils.encoding import smart_str, smart_unicode
#     file = FileDirectory.objects.get(id=file_id)
#     response = HttpResponse(mimetype='application/pdf')
#     response['Content-Disposition'] = 'attachment; filename=%s' % smart_str(file.name.strip())
#     response.write(file.data)
#     return response
