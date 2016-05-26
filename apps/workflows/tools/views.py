from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.shortcuts import render, get_object_or_404
from hr.models import Workflow_object
from workflows.tools.forms import *
import base64
from workflows.models import Workflow,State,Transition,WorkflowPermissionRelation,StatePermissionRelation
from workflows.utils import *
from permissions.utils import register_role,register_permission,has_permission,grant_permission
from permissions.models import Permission,PrincipalRoleRelation
from django.contrib.auth.models import User
from pydot import pydot

def workflow_add(request):
    if request.method == 'POST':
        form = WorkflowAddForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES['file']
            graph = pydot.graph_from_dot_data(file.read())
            workflow = Workflow.objects.create(name = graph.get_name())
            graph.write_png('mysite/media/'+workflow.name+'.png')
            
            nodes = sorted(graph.get_nodes(),key = lambda node:node.get_id())
            for node in nodes:
                state = State.objects.create(name=node.get_name(), workflow= workflow)
                if not node.get_id():
                    #state.status = 'hiden'
                    state.save()
                if node.get_root():
                    workflow.initial_state = state
            
            for edge in graph.get_edges():
                source_state = State.objects.get(name=edge.get_source(),workflow_id=workflow.id)
                destination_state = State.objects.get(name=edge.get_destination(),workflow_id=workflow.id)
                transition= Transition.objects.create(name="Make "+destination_state.name, workflow=workflow, destination=destination_state)
                source_state.transitions.add(transition)
            
            workflow.save()
            
            view = get_object_or_404(Permission, codename='view')
            edit = get_object_or_404(Permission, codename='edit')
    
            WorkflowPermissionRelation.objects.create(workflow=workflow, permission=view)
            WorkflowPermissionRelation.objects.create(workflow=workflow, permission=edit)
            
            return HttpResponseRedirect(reverse('workflows.tools.views.workflows_list'))
    else:
        form = WorkflowAddForm()  # An unbound form
    
    return render_to_response('workflow/workflow_add.html', {
        'form': form,
    }, context_instance=RequestContext(request))
    
def workflow_setpermission(request,workflow_id):
    workflow = get_object_or_404(Workflow, id=workflow_id)
    content = open('mysite/media/'+workflow.name+'.png').read()
    file_data = "data:image/jpeg;base64,"+base64.b64encode(content)
    states = State.objects.filter(workflow_id=workflow.id)
    #permissions = Permission.objects.all().order_by('id')
    view = get_object_or_404(Permission, codename='view')
    edit = get_object_or_404(Permission, codename='edit')
    roles = Role.objects.all().order_by('id')
    if request.method == 'POST':
        for state in states:
            for role in roles:
                relations = StatePermissionRelation.objects.filter(state_id=state.id, permission_id=view.id, role_id=role.id)
                if relations.count() == 0:
                    StatePermissionRelation.objects.create(state=state, permission=view, role=role)
            if request.POST[state.name]:
                selected_role = request.POST[state.name]
                role = get_object_or_404(Role, name=selected_role)
                relations = StatePermissionRelation.objects.filter(state_id=state.id, permission_id=edit.id)
                if relations.count() == 0:
                    StatePermissionRelation.objects.create(state=state, permission=edit, role=role)
                else:
                    relations.update(role=role)
                    
        return HttpResponseRedirect(reverse('workflows.tools.views.workflows_list'))
    
    return render_to_response('workflow/workflow_setpermission.html', {
        'workflow':workflow,'file_data':file_data,
        'states':states,'roles':roles
    }, context_instance=RequestContext(request))

def workflow_object_add(request,workflow_id):
    workflow = get_object_or_404(Workflow, id=workflow_id)
    if request.method == 'POST':  # If the form has been submitted...
        #form = WorkflowObjectAddModelForm(request.POST)  # A form bound to the POST data
        if request.POST['name']:  # All validation rules pass
            workflow_object = Workflow_object.objects.create(name = request.POST['name'])
            set_workflow(workflow_object, workflow)
            
            #grant permission
            roles = Role.objects.all()
            view = get_object_or_404(Permission, codename='view')
            edit = get_object_or_404(Permission, codename='edit')
            for role in roles:
                grant_permission(workflow_object, role, view)
            
            return HttpResponseRedirect(reverse('workflows.tools.views.workflows_list'))
    else:
        form = WorkflowObjectAddForm()  # An unbound form
        
    return render_to_response('workflow/workflow_object_add.html', {
        'form': form,'workflow':workflow,
    }, context_instance=RequestContext(request))
    
def workflow_states_list(request,workflow_id,object_id):
    workflow_object = get_object_or_404(Workflow_object, id=int(object_id))
    workflow = get_workflow(workflow_object)
    user = request.user
    #do_transition(),the transition_id from POST
    if has_permission(workflow_object, user, "edit"):
        if request.method == 'POST':
            if request.POST['transition_id']:
                transition = get_object_or_404(Transition, id=int(request.POST['transition_id']))
                do_transition(workflow_object,transition,user)
                #state = get_object_or_404(State, id=1)
                #set_state(workflow_object,state)
    
    #return current_state and workflow_states to show in page
    current_state = None
    workflow_states = []
    transitions = []
    states = State.objects.filter(workflow_id=workflow.id).order_by('id')
    if has_permission(workflow_object, user, "view"):
        current_state = get_state(workflow_object)
        for state in states:
            #if state.status and 'hiden' in state.status:
            #    continue
            #if "Reject" not in state.name and "Failed" not in state.name and "Success" not in state.name:
            workflow_states.append(state)
    
    if has_permission(workflow_object, user, "edit"):
        transitions = get_allowed_transitions(workflow_object,user)
    
    content = open('mysite/media/'+workflow.name+'.png').read()
    file_data = "data:image/jpeg;base64,"+base64.b64encode(content)
    
    return render_to_response('workflow/states_list.html', {
        'workflow':workflow,'workflow_states':workflow_states,'transitions':transitions,
        'current_state':current_state,'object':workflow_object,'file_data':file_data,
    }, context_instance=RequestContext(request))

def workflows_list(request):
    workflows = Workflow.objects.all().order_by('id')
    return render_to_response('workflow/workflows_list.html', {
        'workflows':workflows,
    }, context_instance=RequestContext(request))

def workflow_show(request,workflow_id):
    workflow = get_object_or_404(Workflow, id=int(workflow_id))
    
    content = open('mysite/media/'+workflow.name+'.png').read()
    file_data = "data:image/jpeg;base64,"+base64.b64encode(content)
    
    workflows = Workflow.objects.all().order_by('id')
    return render_to_response('workflow/workflow_show.html', {
        'workflow':workflow,'file_data':file_data
    }, context_instance=RequestContext(request))

def workflow_objects_list(request,workflow_id):
    #workflows = Workflow.objects.all().order_by('id')
    #workflow_objects = Workflow_object.objects.all().order_by('id')
    workflow = get_object_or_404(Workflow, id=workflow_id)
    workflow_objects = workflow.get_objects()
    return render_to_response('workflow/workflow_objects_list.html', {
        'workflow':workflow,'workflow_objects':workflow_objects
    }, context_instance=RequestContext(request))
