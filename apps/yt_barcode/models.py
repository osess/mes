from django.db import models
from django.utils.translation import ugettext_lazy as _
from yt_object.models import YTObject

class Barcode(models.Model):
    code            = models.CharField(max_length=20, verbose_name=_("code"))
    name            = models.CharField(max_length=20, verbose_name=_("name"))
    base64_code     = models.TextField(verbose_name=_("base64_code"))

    date_added      = models.DateTimeField(auto_now_add=True, verbose_name=_("date_added"))
    date_modified   = models.DateTimeField(auto_now=True, verbose_name=_("date_modified"))
    
    class Meta:
        ordering = ('-date_modified',)
        unique_together = ('code', 'name',)
