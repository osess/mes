'''
Created on Jan 14, 2011

@author: peterm
'''
from warehouse.models import Location
from django import template
register = template.Library()


@register.inclusion_tag('warehouse/tags/show_inventory_locations.html')
def show_inventory_locations(item):
    '''
    Goes through all locations and list their content for the 
    specified item.
    '''
    return {'inventory_locations':item.location_inventory()}

@register.inclusion_tag('warehouse/tags/show_locations.html')
def show_locations():
    locations = Location.objects.all().order_by('code')
    return {'locations_list':locations}

