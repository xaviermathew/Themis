import itertools

from elasticsearch_dsl import Search
from elasticsearch_dsl.connections import connections

from django.conf import settings
from django.shortcuts import render

from themis.news.models import Tweet, Article


def get_search_results(q):
    client = connections.create_connection(hosts=settings.ELASTICSEARCH_HOSTS)
    s = Search(using=client, index="news").filter("term", title=q)
    return s.count(), itertools.islice(s.scan(), 500)


def home(request):
    ctx = {
        'num_docs': Tweet.objects.count() + Article.objects.count()
    }
    q = request.GET.get('q')
    if q:
        ctx['q'] = q
        ctx['num_results'], ctx['results'] = get_search_results(q)
    return render(request, 'base.html', ctx)
