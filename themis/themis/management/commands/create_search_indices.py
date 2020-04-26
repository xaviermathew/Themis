import logging

from elasticsearch_dsl import Document
from elasticsearch_dsl.connections import connections

from django.conf import settings
from django.core.management import BaseCommand
from django.utils.module_loading import autodiscover_modules

_LOG = logging.getLogger(__name__)


class Command(BaseCommand):
    def handle(self, **options):
        autodiscover_modules('search_indices')
        connections.create_connection(hosts=settings.ELASTICSEARCH_HOSTS)
        for search_class in Document.__subclasses__():
            search_class.init()
            _LOG.info('search_class:[%s] initialized', search_class)
