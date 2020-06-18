from rest_framework import mixins, viewsets

from mnemonic.news.search_models import NewsIndex
from mnemonic.news.serializers import NewsIndexSerializer


class NewsIndexViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = NewsIndex.objects.all()
    serializer_class = NewsIndexSerializer
