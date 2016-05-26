from django import forms
from django.utils.translation import ugettext_lazy as _
from companydepartment.models import *

class HRDepartmentAddForm(forms.Form):
    name = forms.CharField(label=_(u"Department Name"), max_length=125)
    belong_to = forms.ModelChoiceField(label=_(u"Belong To Company"), queryset=Company.objects.all())
    parent = forms.ModelChoiceField(label=_(u"Parent"), queryset=Department.objects.all(), required=False)
    description = forms.CharField(label=_(u"Description"), max_length=250, required=False)
    address = forms.CharField(label=_(u"Address"), max_length=125, required=False)
    city = forms.CharField(label=_(u"City"), max_length=50, required=False)
    state = forms.CharField(label=_(u"State"), max_length=10, required=False)
    zip_code = forms.CharField(label=_(u"ZipCode"), max_length=7, required=False)
    importance = forms.IntegerField(label=_(u"Importance"),initial=1)
    
    lft = forms.IntegerField(widget=forms.HiddenInput(), initial=1)
    rght = forms.IntegerField(widget=forms.HiddenInput(), initial=1)
    tree_id = forms.IntegerField(widget=forms.HiddenInput(), initial=1)
    level = forms.IntegerField(widget=forms.HiddenInput(), initial=1)
    
class HRDepartmentAddModelForm(forms.ModelForm):
    class Meta:
        model = Department
    def __init__(self, *args, **kwargs):
        super(HRDepartmentAddModelForm, self).__init__(*args, **kwargs)
        for key in self.fields:
           self.fields[key].label = _(self.fields[key].label)

class HRCompanyAddModelForm(forms.ModelForm):
    class Meta:
        model = Company
    def __init__(self, *args, **kwargs):
        super(HRCompanyAddModelForm, self).__init__(*args, **kwargs)
        for key in self.fields:
           self.fields[key].label = _(self.fields[key].label)
           
    lft = forms.IntegerField(widget=forms.HiddenInput(), initial=1)
    rght = forms.IntegerField(widget=forms.HiddenInput(), initial=1)
    tree_id = forms.IntegerField(widget=forms.HiddenInput(), initial=1)
    level = forms.IntegerField(widget=forms.HiddenInput(), initial=1)
    parent = forms.ModelChoiceField(label=_(u"Parent"), queryset=Company.objects.all(), required=False)
    