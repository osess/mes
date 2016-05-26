# coding=utf-8
'''
from models import Location, Item, ItemJournal, BomEntry, ItemEntry, ItemPrice
from django.contrib import admin

class InitialFieldsMixin(object):

    def get_form(self, request, obj=None, **kwargs):
        form = admin.ModelAdmin.get_form(self, request, obj, **kwargs)
        if not hasattr(self.__class__, 'initial'):
            return form

        old_init = form.__init__
        def new_init(_self, *args, **kwargs):
            if 'instance' not in kwargs:
                for field_name, callback in self.__class__.initial.iteritems():
                    kwargs['initial'][field_name] = callback(self, request,
                                                             obj, **kwargs)
            return old_init(_self, *args, **kwargs)
        form.__init__ = new_init

        return form

class LocationAdmin(admin.ModelAdmin):
    list_display = ('code', 'description', 'lon', 'lat',)


class BomEntryInline(admin.TabularInline):
    model = BomEntry
    fk_name = 'parent'
    
class ItemAdmin(admin.ModelAdmin):
    #initial = {'updated_by': lambda self, request , obj, **kwargs: request.user}
    list_display = ('code', 'description', 'identifier',)
    inlines = [ BomEntryInline, ]
    
    


admin.site.register(Location, LocationAdmin)    
admin.site.register(Item, ItemAdmin)
admin.site.register(ItemJournal)
admin.site.register(ItemEntry)
admin.site.register(ItemPrice)
'''