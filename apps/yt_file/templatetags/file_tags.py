from django import template  
from django.shortcuts import get_object_or_404
from yt_file.models import File
from django.contrib.contenttypes.models import ContentType

register = template.Library()

def xor_decode(value):

    value = (''.join([chr(ord(x) ^ 0x88) for x in value.decode('hex')]))

    return value

register.filter('xor_decode', xor_decode)


def files_for_object(context,object):
    fileowner_type = ContentType.objects.get_for_model(object)
    files = File.objects.filter(content_type__pk=fileowner_type.id,object_id=object.id)
    return {'files': files,'request':context['request']}
register.inclusion_tag('tag_files.html', takes_context=True)(files_for_object)


def file_owner_name(file):
    file_owner_contenttype = get_object_or_404(ContentType, id=file.content_type_id)
    
    file_owner_class = file_owner_contenttype.model_class()
    file_owner_instance = get_object_or_404(file_owner_class, id=file.object_id)
    if hasattr(file_owner_instance, 'name'):
        return file_owner_instance.name
    return ''

register.filter('file_owner_name', file_owner_name)
