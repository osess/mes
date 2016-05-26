'''
Created on Jan 16, 2011

@author: peterm
'''

__all__ = ('SumCase')
from django.db import models

class SQLSumCase(models.sql.aggregates.Aggregate):
    is_ordinal = True
    sql_function = 'SUM'
    sql_template = "%(function)s(CASE %(case)s WHEN %(when)s THEN %(field)s ELSE 0 END)"

    def __init__(self, col, **extra):
        if isinstance(extra['when'], basestring):
            extra['when'] = "'%s'"%extra['when']

        if not extra.get('case', None):
            extra['case'] = '"%s"."%s"'%(extra['source'].model._meta.db_table, extra['source'].name)

        if extra['when'] is None:
            extra['when'] = True
            extra['case'] += ' IS NULL '

        super(SQLSumCase, self).__init__(col, **extra)

class SumCase(models.Aggregate): # TODO
    name = 'SUM'

    def add_to_query(self, query, alias, col, source, is_summary):
        aggregate = SQLSumCase(col, source=source, is_summary=is_summary, **self.extra)
        query.aggregates[alias] = aggregate