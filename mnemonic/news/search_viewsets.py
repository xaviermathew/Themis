from rest_framework_elasticsearch import es_views, es_filters

from mnemonic.news.search_indices import News
from mnemonic.news.utils.search_utils import get_connection


class NewsView(es_views.ListElasticAPIView):
    es_client = get_connection()
    es_model = News
    es_filter_backends = (
        es_filters.ElasticSQSFilter,
        # es_filters.ElasticSearchFilter,
    )
    # es_filter_fields = (
    #     es_filters.ESFieldFilter('author'),
    #     es_filters.ESFieldFilter('title'),
    #     es_filters.ESFieldFilter('body'),
    # )
    # es_search_fields = (
    #     'author',
    #     'title',
    #     'body'
    # )
    es_sqs_fields = (
        'author',
        'title',
        'body'
    )
