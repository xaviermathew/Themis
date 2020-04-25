import operator

from django.db import models

from themis.models import EntityBase


def get_entity_type_choices():
    return reduce(operator.or_, [models.Q(app_label=m._meta.app_label,
                                          model=m._meta.model_name) for m in EntityBase.get_entity_types()])
