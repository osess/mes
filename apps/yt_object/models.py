from django.db import models
from django.utils.translation import ugettext_lazy as _

class YTObject(models.Model):
    date_added      = models.DateTimeField(auto_now_add=True, verbose_name=_("date_added"))
    date_modified   = models.DateTimeField(auto_now=True, verbose_name=_("date_modified"))
    code            = models.CharField(max_length=20, unique=True, verbose_name=_("code"))
    
    class Meta:
        abstract = True
        ordering = ('-date_modified',)
