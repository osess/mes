from django import forms
from django.utils.translation import ugettext_lazy as _
from models import *

class TechnologyRevForm(forms.ModelForm):
    class Meta:
        model = TechnologyRev
        exclude = ('parent', 'child', 'updated_by', 'created_at', 'updated_at', 'order')
    def __init__(self, *args, **kwargs):
        super(TechnologyRevForm, self).__init__(*args, **kwargs)
        for key in self.fields:
           self.fields[key].label = _(self.fields[key].label)
