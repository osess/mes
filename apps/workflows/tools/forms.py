from django import forms
from django.utils.translation import ugettext_lazy as _
from hr.models import *
from workflows.models import Workflow,State,Transition

class RoleAddForm(forms.Form):
    name = forms.CharField(label=_(u"Role Name"), max_length=125)

class WorkflowAddForm(forms.Form):
    file = forms.FileField(label=_(u"File"), required=False)

class WorkflowObjectAddForm(forms.Form):
    name = forms.CharField(label=_(u"Workflow Name"), max_length=125)
    
class WorkflowObjectAddModelForm(forms.ModelForm):
    class Meta:
        model = Workflow_object
    def __init__(self, *args, **kwargs):
        super(HRCompanyAddModelForm, self).__init__(*args, **kwargs)
        for key in self.fields:
           self.fields[key].label = _(self.fields[key].label)
           