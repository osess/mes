'''
Created on 2009-07-04

@author: marcin
'''

from django import template 
from django.core.urlresolvers import reverse
from productcatalog import models 
from django.db.models import Q


class ProductSearch(object):
    title = 'Product search results'
    def keyword_search(self, keyword):
        query = Q(long_desc__icontains=keyword) | \
            Q(short_desc__icontains=keyword) | \
            Q(name__icontains=keyword)
        result = models.Product.objects.published().filter(query)
        return [(p.name, reverse('weboffer-product-page',args=[p.id])) for p in result[:10]]
    def search(self, **kwargs):
        pass
    

class WebofferSummary(object):
    title = "Podsumowanie katalogu ofertowego"
    def render(self):
        data = {
            'products': {
                'published': models.Product.objects.published().count(),
                'overall':  models.Product.objects.count(),
                },
            'categories': {
                'published': models.Category.objects.published().count(),
                'overall': models.Category.objects.count(),
                },
            }
        return template.loader.render_to_string(
                'weboffer/dashboard/summary.html', 
                data)


