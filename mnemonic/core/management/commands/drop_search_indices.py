import logging

from elasticsearch import Elasticsearch

from django.conf import settings
from django.core.management import BaseCommand

_LOG = logging.getLogger(__name__)


class Command(BaseCommand):
    def handle(self, **options):
        es = Elasticsearch(settings.ELASTICSEARCH_HOSTS)
        es.indices.delete(index='_all')
