#-*- coding: UTF-8 -*- 
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpResponse
from django.template import Template, Context
from django.core.urlresolvers import reverse
from django.shortcuts import render, get_object_or_404
from django.utils.simplejson.encoder import JSONEncoder
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import auth
from person.models import Person, Employee, UserPlainPassword

def persons_list(request):
    files = []
    person = None
    persons = Person.objects.filter(user_id = request.user.id)
    contenttype_id = 1
    if len(persons)==1:
        person = persons[0]
        fileowner_type = ContentType.objects.get_for_model(person)
        contenttype_id = fileowner_type.id
        files = File.objects.filter(content_type__pk=fileowner_type.id,object_id=person.id)
        
    return render_to_response('person/persons_list.html', {
        'files': files,'person':person,'contenttype_id':contenttype_id
    }, context_instance=RequestContext(request))


def add_plain_password(username, password):

    try:
        user = UserPlainPassword.objects.get(username = username)
    except:
        user = None

    if user:
        user.password = password
        user.save()
    else:
        new_user = UserPlainPassword.objects.create(
            username = username,
            password = password,
            )
        new_user.save()
