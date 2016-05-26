from django.db import models
from django.contrib.auth.models import User
from warehouse.models import DeviceEntry
from django.utils.translation import ugettext_lazy as _



class Maintenance(models.Model):

    device = models.ForeignKey(DeviceEntry, related_name="maintenances", verbose_name=_("device"))
    date = models.DateField(verbose_name=_("maintenance date"))
    project = models.CharField(_('maintenance project'), max_length=255)
    status = models.CharField(_('maintenance status'), max_length=255)
    maintainer = models.ForeignKey(User, related_name="maintainer_maintance", verbose_name=_("maintainer"))
    applicat = models.ForeignKey(User, related_name="applicat_maintance", verbose_name=_("maintenance applicat"))

    class Meta:
        verbose_name = _('Maintenance')
        verbose_name_plural = _('Maintenance')

    def __unicode__(self):

        return u'%s' % (self.device)

