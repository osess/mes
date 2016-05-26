# coding=utf-8
'''
Created on Jan 12, 2011

@author: peterm
'''
from django.forms import ModelForm
from django.utils.translation import ugettext_lazy as _
from models import Item, BomEntry, TransferList, DeviceEntry, ItemEntry
from django import forms
import datetime
from django.contrib.auth.models import User
from django.db.models import Q

class ItemForm(ModelForm):
    class Meta:
        model = Item
        exclude = ('updated_by')

class BomEntryForm(ModelForm):
    class Meta:
        model = BomEntry
        exclude = ('updated_by', 'productionline', 'state', 'parent')




class TransferListForm(ModelForm):
            # applicat = forms.ModelChoiceField(queryset=User.objects.all(), label=_(u"applicat transfer_list"), widget = forms.PasswordInput())
    user = forms.CharField(label=_(u"applicat transfer_list"), widget = forms.PasswordInput())
    accept_date = forms.DateField(initial=datetime.date.today, label=_(u"accept_date transfer_list"))
    # tools = Item.objects.filter(content_type__model = "tool")

    # print tools
    device_entries = forms.ModelMultipleChoiceField(queryset=DeviceEntry.objects.filter(Q(item__content_type__model = 'tool') | Q(item__content_type__model = 'knife' )))
    # print DeviceEntry.objects.filter(item = tools)
    class Meta:
        model = TransferList
        fields = ['user', 'accept_date', 'transfer_category', 'state', 'device_entries']
        widgets = {
            # 'applicat': forms.PasswordInput(),
            # 'accept_date': initial=datetime.date.today,
            # 'device_entries': 'm2m_transfer'
        }





