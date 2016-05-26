#-*- coding:UTF-8 -*-
import xadmin
from xadmin.layout import *
from xadmin.plugins.inline import Inline
from django.utils.translation import ugettext_lazy as _

from models import *
from yt_barcode.views import BatchBarcodeAction

class CategoryAdmin(object):
    model_icon = 'cog'
    hidden_menu = False
    show_bookmarks = False
    list_display = (
       'name', 'parent', 'description', 'photo',
       'is_published', 'ext_code', 'custom1', 'custom2',
       'custom3', 'custom4')

    search_fields = ['name']
    list_filter = ['name', 'parent', 'description', 'photo',
       'is_published', 'ext_code', 'custom1', 'custom2',
       'custom3', 'custom4']


class AttributeAdmin(object):
    model_icon = 'cog'
    hidden_menu = False
    active_menu = "storage"
    show_bookmarks = False
    list_display = (
       'name', 'unit', 'ext_code')

    list_filter = ['name', 'unit', 'ext_code']
    search_fields = ['name', 'unit', 'ext_code']


class GroupAdmin(object):
    model_icon = 'cog'
    hidden_menu = False
    show_bookmarks = False
    list_display = (
       'name', 'symbol')

    list_filter = ['name', 'symbol']
    search_fields = ['name']

class ProductAttributeInline(object):
    model = ProductAttribute
    extra = 1
    style = 'table'
    exclude = ['display_value','is_published', 'ext_code']

class ProductAdmin(object):
    model_icon = 'cog'
    hidden_menu = False
    show_bookmarks = False
    list_display_links = ('name',)
    list_display_links_details = True
    list_display = (
        'name', 'cad_code', 'symbol', 'norm_code', 'category', 'short_desc', 'long_desc', 'ext_code',
        'groups', 'created_at', 'updated_at', 'is_published',
    )

    list_filter = [
        'cad_code', 'category', 'name', 'short_desc','long_desc', 'is_published',
        'ext_code', 'type', 'groups', 'attributes', 'created_at', 'updated_at',
    ]
    search_fields = ['cad_code',]

    exclude = ['is_published', 'ext_code', 'type', 'custom1', 'custom2', 'custom3', 'custom4', 'groups']

    Inline(ProductAttribute)
    inlines = [ProductAttributeInline]

    actions = [BatchBarcodeAction]

class ProductPhotoAdmin(object):
    model_icon = 'cog'
    hidden_menu = False
    show_bookmarks = False
    list_display = (
       'product', 'image', 'display_order', 'created_at',
       'updated_at')

    list_filter = ['product', 'image', 'display_order', 'created_at',
       'updated_at']
    search_fields = ['product']


class ProductAttributeAdmin(object):
    model_icon = 'cog'
    hidden_menu = False
    active_menu = "storage"
    show_bookmarks = False
    list_display = (
       'product', 'attribute', 'display_value', 'absolute_value',
       'is_published', 'ext_code'
       )

    list_filter = ['product', 'attribute', 'display_value', 'absolute_value',
       'is_published', 'ext_code']
    search_fields = ['product']


xadmin.site.register(Category, CategoryAdmin)
xadmin.site.register(Attribute, AttributeAdmin)
xadmin.site.register(Group, GroupAdmin)
xadmin.site.register(Product, ProductAdmin)
xadmin.site.register(ProductPhoto, ProductPhotoAdmin)
xadmin.site.register(ProductAttribute, ProductAttributeAdmin)



'''
from django.conf import settings
from django import db
try:
    from tabbedadmin.admin import TabbedModelAdmin
except ImportError, e:
    import warnings
    warnings.warn('django-tabbed-admin is not installed - disabling support for native tabs')
    TabbedModelAdmin = admin.ModelAdmin
'''

'''
class CategoryAdmin(object):
    list_display = ('id','name','parent','is_published')
    list_display_links = ('id','name')
    list_filter  = ('parent','is_published')
    search_fields = ('name','description',)
    actions = ['publish', 'hide', 'delete_selected']
    # change_list_template = 'admin/weboffer/category/change_list.html'

    class Media:
        css = { 'screen': ('admin/css/admin.css',) }
    
    def changelist_view(self, request, extra_context=None):
        extra_context=extra_context or dict()
        extra_context.update({
            'navpath': self.get_navigation_path(request),
            })

        return super(CategoryAdmin, self).changelist_view(request, extra_context)

    def get_navigation_path(self, request):
        id = request.GET.get('parent__id__exact')
        if not id:
            return []
        c = Category.objects.get(id=id)
        path = [c]
        while c.parent:
            path.append(c.parent)
            c = c.parent
        path.reverse()
        return path
        

    def navigation(self, request):
        model = self.model
        opts = model._meta

        def render(obj):
            parent, children = obj
            template = loader.get_template('cms/navigation_item.html')
            content = template.render(Context({'page': parent}))
            return '<li id="navigation-%s">%s%s</li>' % (parent.id, content, children and '<ul>%s</ul>'%''.join([render(child) for child in children]) or '')

        return render_to_response('navigation.html')

    def publish(self, request, changelist):
        selected = request.POST.getlist(CHECKBOX_NAME)
        objects = changelist.get_query_set().filter(pk__in=selected)
        for obj in objects:
            obj.is_published = True
            obj.save()
        self.message_user(request, _("Categories were published"))
    publish.short_description = _('Publish selected categories')

    def hide(self, request, changelist):
        selected = request.POST.getlist(CHECKBOX_NAME)
        objects = changelist.get_query_set().filter(pk__in=selected)
        for obj in objects:
            obj.is_published = False
            obj.save()
        self.message_user(request, _("Categories were hidden"))
    hide.short_description = _('Hide selected categories')


class ProductAttributesInline(object):
    model = ProductAttribute
    extra = 1


class ProductPhotosInline(object):
    model = ProductPhoto
    template = "admin/weboffer/edit_inline/photos.html"
    extra = 1
    exclude = ('display_order',)


class ProductAdmin(object):

    def attributes_values(self, instance):
        attribute_values = ''
        for attribute_value in instance.product_attributes.all():
            attribute_values += attribute_value.attribute.name
            attribute_values += ':'
            attribute_values += str(attribute_value.absolute_value)
            attribute_values += ' | '
        return attribute_values
    attributes_values.short_description = _("attribute")
    attributes_values.allow_tags = True
    attributes_values.is_column = True

    class Media:
        css = {
                'all': (settings.ADMIN_MEDIA_PREFIX+'/weboffer/product.css',),
                }
    list_display = ('symbol','name','category','attributes_values')
    list_display_links = ('id','symbol','name')
    list_filter  = ('category','is_published')
    search_fields = ('name','id','short_desc','long_desc',)
    actions = ['publish', 'hide', 'delete_selected']
    tabs_order = ['common','attributes','photos','customfields','integration']
    tabs = {
       'common': {
           'title': _('Common'),
           'fieldsets': (
               (_('Common'), {
                    'fields': ['symbol', 'name', 'short_desc',],
                    'classes': ('left',),
                    }),
               (_('Publication'), {
                    'fields': ['is_published', 'category', 'groups',],
                    'classes': ('right',),
                    }),
               (None, {'fields': ['long_desc',]}),
               )
           },
       'attributes': {
           'title': _('Attributes'),
           'fieldsets': (),
           'inlines': [ ProductAttributesInline ],
           },
       'photos': {
           'title': _('Photos'),
           'fieldsets': (),
           'inlines': [ ProductPhotosInline ],
           },
       'customfields': {
           'title': _('Custom fields'),
           'fieldsets': (
               (None, {'fields': ['custom1','custom2','custom3','custom4',]}),
               )
           },
       'integration': {
           'title': _('Integration'),
           'fieldsets': (
               (None, {'fields': ['ext_code'],}),
               )
           },
       }

    def publish(self, request, changelist):
        selected = request.POST.getlist(CHECKBOX_NAME)
        objects = changelist.get_query_set().filter(pk__in=selected)
        for obj in objects:
            obj.is_published = True
            obj.save()
        self.message_user(request, _("Products were published"))
    publish.short_description = _('Publish selected products')

    def hide(self, request, changelist):
        selected = request.POST.getlist(CHECKBOX_NAME)
        objects = changelist.get_query_set().filter(pk__in=selected)
        for obj in objects:
            obj.is_published = False
            obj.save()
        self.message_user(request, _("Products were hidden"))
    hide.short_description = _('Hide selected products')

    def changelist_view(self, request, extra_context=None):
        #widget = TreeView()
        #extra_context = extra_context or {
        #        'category_tree': widget.render('category_tree',Category,{'parent_field_name': 'parent',}),
        #        }
        return super(ProductAdmin, self).changelist_view(request, extra_context)

class ProductPhotoAdmin(object):
    model_icon = 'cog'
    hidden_menu = False
    list_display = (
       'product', 'image', 'display_order', 'created_at',
       'updated_at')

    list_filter = ['product', 'image', 'display_order', 'created_at',
       'updated_at']
    search_fields = ['product']


class ProductAttributeAdmin(object):
    model_icon = 'cog'
    hidden_menu = False
    list_display = (
       'product', 'attribute', 'display_value', 'absolute_value',
       'is_published', 'ext_code'
       )

    list_filter = ['product', 'attribute', 'display_value', 'absolute_value',
       'is_published', 'ext_code']
    search_fields = ['product']

xadmin.site.register(Attribute)
xadmin.site.register(Product, ProductAdmin)
xadmin.site.register(Category, CategoryAdmin)
xadmin.site.register(Group)
xadmin.site.register(ProductPhoto, ProductPhotoAdmin)
xadmin.site.register(ProductAttribute, ProductAttributeAdmin)
'''

