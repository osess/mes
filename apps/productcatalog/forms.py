from django import forms 
from django.forms.models import BaseInlineFormSet
from django.forms.formsets import formset_factory
import models


class BaseProductPhotoFormset(BaseInlineFormSet):
    def add_fields(self, form, index):
        super(BaseProductPhotoFormset, self).add_fields(form, index)
        form.fields["my_field"] = forms.CharField()


class ProductPhotoEdit(forms.ModelForm):
    class Meta:
        model = models.ProductPhoto
        fields = ('image',)

#ProductPhotoFormset = formset_factory(NewProductPhoto, formset=BaseProductPhotoFormset)
