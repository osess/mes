from django.conf import settings

from pinax.apps.account.models import Account, AnonymousAccount
#from django.contrib.gis.utils import GeoIP

def start(request):
    #g = GeoIP()
    real_ip = None;
    geo = None
    try:
        real_ip = request.META['HTTP_X_FORWARDED_FOR']
        #real_ip = request.META['REMOTE_ADDR']
    except:
        #real_ip = '82.197.131.84'
        pass
    #if real_ip != None:
    #    geo = g.city(real_ip)

    #geo = None
    if geo == None:
        geo = {'latitude': 37.4419, 'longitude': 122.1419, 'city': 'Shanghai', 'country_name': 'New Zealand'}
    return {
            "version": settings.VERSION,
            #"GOOGLE_MAPS_API_KEY": settings.GOOGLE_MAPS_API_KEY,
            "geo": geo,
    }
