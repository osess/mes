from django.contrib.sites.models import get_current_site
from settings import BRAND_VIEW

class VoiceMixin(object):
    def get_context_data(self, **kwargs):
        context = super(VoiceMixin, self).get_context_data(**kwargs)
        context.update({
            'site': get_current_site(self.request),
            'brand_view': BRAND_VIEW
        })

        return context
