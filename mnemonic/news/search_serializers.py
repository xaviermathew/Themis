from rest_framework_elasticsearch.es_serializer import ElasticModelSerializer

from mnemonic.news.search_indices import News


class NewsSerializer(ElasticModelSerializer):
    class Meta:
        es_model = News
        fields = ('author', 'title', 'body', 'score')
