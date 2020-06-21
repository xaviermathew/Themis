from django.conf.urls import url

from mnemonic.news import search_viewsets

urlpatterns = [
    url(r'news/search', search_viewsets.NewsView.as_view()),
]
