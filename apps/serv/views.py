# Create your views here.
from django.shortcuts import render_to_response
from django.shortcuts import get_object_or_404
from django.shortcuts import get_list_or_404
from django.http import HttpResponseRedirect,HttpResponse, Http404
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.decorators import login_required
from django.utils.simplejson.encoder import JSONEncoder

from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType

from django.conf import settings

from django.db.models import Q
import operator
import settings

#from geopy import geocoders 

#def homepage(request, template_name="homepage.html"):
def homepage(request, template_name="homepage_mes.html"):
    real_ip = None;
    geo = None
    try:
        real_ip = request.META['HTTP_X_FORWARDED_FOR']
    except:
        pass

    if request.user.is_authenticated():
        template_name ="dashboard.html"
    return render_to_response(template_name,
        {
     #       "GOOGLE_MAPS_API_KEY": settings.GOOGLE_MAPS_API_KEY,
     #       "geo": geo,
    #        "real_ip":real_ip,
        }, context_instance=RequestContext(request))

'''
from gen.models import *
def create(request, template_name="serv/main_create.html"):
    woochee_entity_types = Entity_Subtypes.objects.all()[10:10000]
    public_entity_types = Entity_Subtypes.objects.filter(pk__gt=10000)
    return render_to_response(template_name,
        {
     #       "GOOGLE_MAPS_API_KEY": settings.GOOGLE_MAPS_API_KEY,
     #       "geo": geo,
    #        "real_ip":real_ip,
            "wc_et": woochee_entity_types,
            "public_et": public_entity_types,
        }, context_instance=RequestContext(request))
'''