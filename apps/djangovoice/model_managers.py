from django.db import models


class StatusManager(models.Manager):
    def get_default(self):
        if not self.count():
            default_status = None
        elif self.filter(default=True).exists():
            default_status = self.filter(default=True)[0]
        else:
            default_status = Status.objects.all()[0]

        return default_status
