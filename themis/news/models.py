from __future__ import unicode_literals

from time import mktime, struct_time
from datetime import datetime
import logging
import urllib.parse as urlparse

import feedparser
import requests

from django.conf import settings
from django.contrib.postgres.fields import JSONField
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
from django.db.utils import IntegrityError

from entity.models import EntityBase, Person
from news.search_indices import NewsIndexable
from themis.models import BaseModel

_LOG = logging.getLogger(__name__)


class JSONWithTimeEncoder(DjangoJSONEncoder):
    def default(self, obj):
        if isinstance(obj, struct_time):
            obj = datetime.fromtimestamp(mktime(obj))
        return super(JSONWithTimeEncoder, self).default(obj)


class NewsSource(EntityBase):
    pass


class Feed(BaseModel):
    name = models.TextField()
    url = models.URLField()
    source = models.ForeignKey(NewsSource, on_delete=models.CASCADE)
    is_top_news = models.BooleanField()

    def __str__(self):
        return '%s:%s' % (self.source, self.name)

    def crawl_feed(self):
        d = feedparser.parse(self.url)
        for entry in d['entries']:
            url = entry.pop('link')
            try:
                a = Article.objects.create(feed=self,
                                           url=url,
                                           title=entry.pop('title'),
                                           body=entry.pop('summary'),
                                           published_on=entry.pop('published_parsed'),
                                           is_top_news=self.is_top_news,
                                           metadata=entry)
            except IntegrityError as ex:
                _LOG.info('Article with url:[%s] may already exist', url, ex)
            else:
                _LOG.info('Article created with url:[%s]', url)
                a.process_async()

    def crawl_feed_async(self):
        from news.tasks import crawl_feed_async
        crawl_feed_async.apply_async(kwargs={'feed_id': self.pk},
                                     queue=settings.CELERY_TASK_QUEUE_CRAWL_FEED,
                                     routing_key=settings.CELERY_TASK_ROUTING_KEY_CRAWL_FEED)


class Article(BaseModel, NewsIndexable):
    NEWS_TITLE_FIELD = 'title'
    NEWS_BODY_FIELD = 'body'

    feed = models.ForeignKey(Feed, on_delete=models.CASCADE)
    url = models.URLField(unique=True, max_length=512)
    title = models.TextField()
    body = models.TextField(blank=True, null=True)
    published_on = models.DateField()
    is_top_news = models.BooleanField(default=False)
    metadata = JSONField()

    def __str__(self):
        return '%s:%s' % (self.feed, self.title)

    def save(self, *args, **kwargs):
        if self.feed.source == 'Google News India':
            parsed = urlparse.urlparse(self.url)
            if parsed.netloc == 'news.google.com':
                self.url = urlparse.parse_qs(parsed.query)['url'][0]
        super(Article, self).save(*args, **kwargs)

    def process(self):
        # r = requests.get(self.url)
        # html = r._content
        _LOG.info('article:[%s] - downloaded url:[%s]', self.pk, self.url)

    def process_async(self):
        from news.tasks import process_article_async
        process_article_async.apply_async(kwargs={'article_id': self.pk},
                                          queue=settings.CELERY_TASK_QUEUE_PROCESS_ARTICLE,
                                          routing_key=settings.CELERY_TASK_ROUTING_KEY_PROCESS_ARTICLE)


class Tweet(BaseModel, NewsIndexable):
    NEWS_TITLE_FIELD = 'tweet'

    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    tweet_id = models.BigIntegerField(unique=True)
    tweet = models.TextField()
    published_on = models.DateTimeField()
    metadata = JSONField()

    def __str__(self):
        return '%s: %s' % (self.person, self.tweet)

    def process(self):
        _LOG.info('processed tweet:[%s][%s]', self.pk, self.tweet_id)

    def process_async(self):
        from news.tasks import process_tweet_async
        process_tweet_async.apply_async(kwargs={'tweet_id': self.pk},
                                          queue=settings.CELERY_TASK_QUEUE_PROCESS_TWEET,
                                          routing_key=settings.CELERY_TASK_ROUTING_KEY_PROCESS_TWEET)
