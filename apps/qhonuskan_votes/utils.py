from django.db.models import aggregates
from django.db.models.sql import aggregates as sql_aggregates
from qhonuskan_votes.models import _vote_models


def get_vote_model(model_name):
    if model_name in _vote_models:
        return _vote_models[model_name]
    else:
        raise Exception('No such vote model "%s"' % model_name)


class SumWithDefault(aggregates.Aggregate):
    name = 'SumWithDefault'


class SQLSumWithDefault(sql_aggregates.Sum):
    sql_template = 'COALESCE(%(function)s(%(field)s), %(default)s)'

setattr(sql_aggregates, 'SumWithDefault', SQLSumWithDefault)
