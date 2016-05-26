from django import forms
from django.utils.translation import ugettext_lazy as _

class UploadFileForm(forms.Form):
    display_name = forms.CharField(label=_(u"Display Name"), max_length=20, required=False)
    path         = forms.CharField(label=_(u"file path"), max_length=20, required=False)
    file         = forms.FileField(label=_(u"File"),)
    