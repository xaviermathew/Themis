from rest_framework import mixins, viewsets

from themis.news.search_models import NewsIndex
from themis.news.serializers import NewsIndexSerializer


class NewsIndexViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = NewsIndex.objects.all()
    serializer_class = NewsIndexSerializer
