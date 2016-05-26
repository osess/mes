from django.contrib.sites.models import Site
from .settings import BRAND_VIEW


def get_voice_extra_context():
    """
    Receives djangovoice extra contexts to view context variable params.
    """
    if Site._meta.installed:
        current_site = Site.objects.get_current()

    else:
        current_site = None

    context = {
        'site': current_site,
        'brand_view': BRAND_VIEW
    }

    return context
