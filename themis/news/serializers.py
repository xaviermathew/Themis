from rest_framework import serializers

from themis.news.search_models import NewsIndex


class NewsIndexSerializer(serializers.ModelSerializer):
    class Meta:
        model = NewsIndex
        fields = ['author', 'title', 'body', 'score']
