from django.db import models

from themis.core.models import BaseModel


class EntityBase(BaseModel):
    name = models.TextField(unique=True)

    class Meta:
        abstract = True

    def __str__(self):
        return self.name

    @staticmethod
    def get_entity_types():
        return EntityBase.__subclasses__()
