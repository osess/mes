from django.db import models

class ProductQuerySet(models.query.QuerySet):
    def published(self):
        return self.filter(is_published=True)


class ProductManager(models.Manager):
    def get_query_set(self):
        return ProductQuerySet(self.model)

    def from_group(self, group):
        """
        get products from group
        """

        # check if group is a int or Group instance
        if isinstance(group, (int, models.Model)):
            return self.get_query_set().filter(groups__exact=group)

        # assume group as string
        return self.get_query_set().filter(groups__symbol__exact=str(group))

    def get_by_extcode(self, ext_code):
        return self.get_query_set().get(ext_code=ext_code)

    def get_by_symbol(self, symbol):
        return self.get_query_set().get(symbol=symbol)

    def from_request(self, request):
        return filter.process(data)


class PublishedProductsManager(ProductManager):
    def get_query_set(self):
        return ProductQuerySet(self.model).published()


class ProductAttributeManager(models.Manager):
    def published(self):
        return self.get_query_set().filter(is_published=True)


class CategoryManager(models.Manager):
    def published(self):
        return self.get_query_set().filter(is_published=True)

    def get_by_extcode(self, ext_code):
        return self.get_query_set().get(ext_code=ext_code)

    def get_by_symbol(self, symbol):
        return self.get_query_set().get(symbol=symbol)

    def subcategories(self, category, level=5):
        return self.get_query_set()


