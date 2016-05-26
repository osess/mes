from tastypie.resources import ModelResource
from manufactureplan.models import ManufactureItem


class MyModelResource(ModelResource):
    class Meta:
        queryset = ManufactureItem.objects.all()
        allowed_methods = ['get']