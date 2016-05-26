
from productcatalog import models
from django.views.generic.list_detail import object_list, object_detail


def list(request, category_slug=None, template_name=None, queryset=None,
        paginate_by=25, extra_context=None, content_processors=None):

    queryset = queryset or models.Product.public_objects.all()
    if category_slug:
        queryset.filter(category__slug=slug)

    return object_list(request, queryset=queryset,
            paginate_by = paginate_by or 25,
            template_name=template_name or 'weboffer/product/list.html',
            content_processors = content_processors,
            extra_context = extra_context,
            template_object_name='product')


def detail(request, id=None, slug=None, template_name=None, queryset=None):
    queryset = queryset or models.Product.public_objects.all()
    return object_detail(request, object_id=id, slug=slug, 
            template_name = template_name or 'weboffer/product/detail.html',
            queryset=queryset, template_object_name='product')


def search(request, keyword, queryset=None, **kwargs):
    return list(request, queryset, **kwargs)
