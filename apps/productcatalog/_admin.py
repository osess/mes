from django.contrib import admin
from django.utils.translation import ugettext as _
from django.conf import settings

from django import db

from models import *
import forms


try:
    from tabbedadmin.admin import TabbedModelAdmin
except ImportError, e:
    import warnings
    warnings.warn('django-tabbed-admin is not installed - disabling support for native tabs')
    TabbedModelAdmin = admin.ModelAdmin



class CategoryAdmin(admin.ModelAdmin):
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


class ProductAttributesInline(admin.TabularInline):
    model = ProductAttribute
    extra = 1


class ProductPhotosInline(admin.StackedInline):
    model = ProductPhoto
    template = "admin/weboffer/edit_inline/photos.html"
    extra = 1
    exclude = ('display_order',)


class ProductAdmin(TabbedModelAdmin):
    class Media:
        css = {
                'all': (settings.ADMIN_MEDIA_PREFIX+'/weboffer/product.css',),
                }
    list_display = ('id','symbol','name','category','is_published')
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

admin.site.register(Attribute)
admin.site.register(Product, ProductAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Group)

