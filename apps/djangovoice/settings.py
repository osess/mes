from django.conf import settings

BRAND_VIEW = getattr(settings, 'VOICE_BRAND_VIEW', 'djangovoice_home')
ALLOW_ANONYMOUS_USER_SUBMIT = getattr(
    settings, 'VOICE_ALLOW_ANONYMOUS_USER_SUBMIT', False)
