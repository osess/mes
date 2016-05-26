#-*- coding: UTF-8 -*- 
from django.db import models
from extensions.custom_fields.encrypt import Base64Field,XORField
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import get_language_from_request, ugettext_lazy as _
from django.contrib.contenttypes import generic
from django.core.files.storage import FileSystemStorage
from settings import UPLOAD_ROOT
upload_storage = FileSystemStorage(location=UPLOAD_ROOT)

class File(models.Model):
    name = models.CharField(max_length=20, blank=True, null=True, verbose_name=_('file name'))
    path = models.CharField(max_length=20, blank=True, null=True, verbose_name=_('file path'))
    display_name = models.CharField(max_length=20, blank=True, null=True, verbose_name=_('display name'))
    code = models.CharField(max_length=30, blank=True, null=True, verbose_name=_("file code"))
    data = Base64Field()
    size = models.CharField(max_length=250, blank=True, unique=False, verbose_name=_("size"))
    type = models.CharField(max_length=250, blank=True, unique=False, verbose_name=_("type"))
    imgtag = models.IntegerField(default=0, blank=True, null=True, verbose_name=_("imgtag"))
    status = models.IntegerField(default=1, blank=True, null=True, verbose_name=_("status"))
    date_added = models.DateTimeField(auto_now_add=True, verbose_name=_("date_added"))
    date_modified = models.DateTimeField(auto_now=True, verbose_name=_("date_modified"))

    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    file = generic.GenericForeignKey('content_type', 'object_id')

    def __unicode__(self):
        return "%s" %(self.display_name)

    class Meta:
        permissions = (
            ("open_file", "Can open file"),
        )

class FileDirectory(models.Model):
    def content_file_name(instance, filename):
        directory_name = ""
        if instance.content_type.model == "technology":
            directory_name = instance.file.product.cad_code
        elif instance.content_type.model == "operationgroup":
            directory_name = instance.file.technology.product.cad_code
        return '/'.join([directory_name, filename])

    name = models.CharField(max_length=20, blank=True, null=True, verbose_name=_('file name'))
    path = models.CharField(max_length=20, blank=True, null=True, verbose_name=_('file path'))
    display_name = models.CharField(max_length=20, blank=True, null=True, verbose_name=_('display name'))
    code = models.CharField(max_length=30, blank=True, null=True, verbose_name=_("file code"))
    data = models.FileField(storage=upload_storage, upload_to=content_file_name)
    size = models.CharField(max_length=250, blank=True, unique=False, verbose_name=_("size"))
    type = models.CharField(max_length=250, blank=True, unique=False, verbose_name=_("type"))
    imgtag = models.IntegerField(default=0, blank=True, null=True, verbose_name=_("imgtag"))
    status = models.IntegerField(default=1, blank=True, null=True, verbose_name=_("status"))
    date_added = models.DateTimeField(auto_now_add=True, verbose_name=_("date_added"))
    date_modified = models.DateTimeField(auto_now=True, verbose_name=_("date_modified"))
    # 是否可用,是否为删除状态
    is_active = models.BooleanField(default=True,verbose_name="is active")

    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    file = generic.GenericForeignKey('content_type', 'object_id')

    def __unicode__(self):
        return "%s" %(self.display_name)

    def set_file_to_delete(self,*args,**kwargs):
        self.is_active = False
        super(FileDirectory,self).save(*args,**kwargs)