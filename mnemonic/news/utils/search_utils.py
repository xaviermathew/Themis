import copy
import itertools

from elasticsearch_dsl import Search
from elasticsearch_dsl.connections import connections

from django.conf import settings

ES_CLIENT = None


def get_connection():
    global ES_CLIENT
    if ES_CLIENT is None:
        ES_CLIENT = connections.create_connection(hosts=settings.ELASTICSEARCH_HOSTS)
    return ES_CLIENT


def get_client():
    client = get_connection()
    return Search(using=client, index="news")


def serializer_search_results(results):
    for result in results:
        d = copy.deepcopy(result._d_)
        d['meta'] = copy.deepcopy(result.meta._d_)
        yield d


def get_search_results(q):
    client = get_client()
    s = client.filter("simple_query_string", query=q, fields=['title', 'source', 'body'])
    results = itertools.islice(s.scan(), 500)
    serialized = serializer_search_results(results)
    return s.count(), serialized
