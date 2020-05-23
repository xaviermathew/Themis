from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search

from django.shortcuts import render

from themis.news.models import Tweet, Article


def get_search_results(q):
    client = Elasticsearch()
    s = Search(using=client, index="news").filter("term", title=q)
    return s.execute()


def home(request):
    ctx = {
        'num_docs': Tweet.objects.count() + Article.objects.count()
    }
    if request.GET.get('q'):
        ctx['results'] = get_search_results(request.GET['q'])
    return render(request, 'base.html', ctx)
