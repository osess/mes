"""
@author: Marcin Nowak
@license: BSD
"""

from django_widgets import Widget
import models

class ProductList(Widget):
    """
    general widget for product lists
    """

    def get_query_set(self, value, options):
        """
        value is a queryset, list or any iterable
        """
        return value

    def get_context(self, products, options):
        """
        returns context to template
        """
        qs = self.get_query_set(products, options)

        if options.has_key('limit'):
            qs = qs[:options['limit']]

        return {
                'products': qs,
                }


class ProductsInGroup(ProductList):
    """
    display products from specified group
    """
    def get_query_set(self, value, options):
        return models.Product.objects.from_group(value).published()


