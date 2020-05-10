from __future__ import unicode_literals

from time import mktime, struct_time
from datetime import datetime
import logging
import urllib.parse as urlparse

import feedparser

from django.conf import settings
from django.contrib.postgres.fields import JSONField
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
from django.db.utils import IntegrityError

from themis.entity.models import EntityBase, Person
from themis.news.search_indices import NewsIndexable
from themis.core.models import BaseModel

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
            published_on_struct = entry.pop('published_parsed')
            published_on = datetime.fromtimestamp(mktime(published_on_struct))
            try:
                a = Article.objects.create(feed=self,
                                           url=url,
                                           title=entry.pop('title'),
                                           summary=entry.pop('summary'),
                                           published_on=published_on,
                                           is_top_news=self.is_top_news,
                                           metadata=entry)
            except IntegrityError as ex:
                _LOG.info('Article with url:[%s] may already exist', url, ex)
            else:
                _LOG.info('Article created with url:[%s]', url)
                a.process_async()

    def crawl_feed_async(self):
        from themis.news.tasks import crawl_feed_async
        crawl_feed_async.apply_async(kwargs={'feed_id': self.pk},
                                     queue=settings.CELERY_TASK_QUEUE_CRAWL_FEED,
                                     routing_key=settings.CELERY_TASK_ROUTING_KEY_CRAWL_FEED)


class Article(BaseModel, NewsIndexable):
    NEWS_TITLE_FIELD = 'title'
    NEWS_BODY_FIELD = 'body'

    feed = models.ForeignKey(Feed, on_delete=models.CASCADE)
    url = models.URLField(unique=True, max_length=512)
    title = models.TextField()
    summary = models.TextField(blank=True, null=True)
    body = models.TextField(blank=True, null=True)
    published_on = models.DateField()
    is_top_news = models.BooleanField(default=False)
    metadata = JSONField()
    is_pushed_to_index = models.BooleanField(default=False)

    def __str__(self):
        return '%s:%s' % (self.feed, self.title)

    def save(self, *args, **kwargs):
        if self.feed.source == 'Google News India':
            parsed = urlparse.urlparse(self.url)
            if parsed.netloc == 'news.google.com':
                self.url = urlparse.parse_qs(parsed.query)['url'][0]
        super(Article, self).save(*args, **kwargs)

    def process(self):
        from themis.news.utils.article_utils import get_body_from_article

        save_fields = []
        if self.body is None:
            self.body = get_body_from_article(self.url)
            save_fields.append('body')
        if not self.is_pushed_to_index:
            self.push_to_index()
            self.is_pushed_to_index = True
            save_fields.append('is_pushed_to_index')
        if save_fields:
            self.save(update_fields=save_fields)
            _LOG.info('article:[%s] - processed url:[%s]', self.pk, self.url)

    def process_async(self):
        from themis.news.tasks import process_article_async
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
    is_pushed_to_index = models.BooleanField(default=False)

    def __str__(self):
        return '%s: %s' % (self.person, self.tweet)

    def get_index_data(self):
        d = super(Tweet, self).get_index_data()
        d['author'] = self.person.name
        return d

    def process(self):
        if not self.is_pushed_to_index:
            self.push_to_index()
            self.is_pushed_to_index = True
            self.save()
            _LOG.info('processed tweet:[%s][%s]', self.pk, self.tweet_id)

    def process_async(self):
        from themis.news.tasks import process_tweet_async
        process_tweet_async.apply_async(kwargs={'tweet_id': self.pk},
                                          queue=settings.CELERY_TASK_QUEUE_PROCESS_TWEET,
                                          routing_key=settings.CELERY_TASK_ROUTING_KEY_PROCESS_TWEET)
