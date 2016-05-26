from django import forms
from django.utils.translation import ugettext_lazy as _
from customer.models import Customer

class CustomerModelForm(forms.Form):
    class Meta:
        model = Customer
    