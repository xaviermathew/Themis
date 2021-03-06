from __future__ import unicode_literals

from time import mktime, struct_time
from datetime import datetime
import logging
import urllib.parse as urlparse

import feedparser

from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.postgres.fields import JSONField
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
from django.db.utils import IntegrityError
from django.utils.functional import cached_property

from mnemonic.entity.models import EntityBase
from mnemonic.news.search_indices import NewsIndexable
from mnemonic.core.models import BaseModel
from mnemonic.news.utils.queryset_utils import CachedManager

_LOG = logging.getLogger(__name__)


class JSONWithTimeEncoder(DjangoJSONEncoder):
    def default(self, obj):
        if isinstance(obj, struct_time):
            obj = datetime.fromtimestamp(mktime(obj))
        return super(JSONWithTimeEncoder, self).default(obj)


class NewsSource(EntityBase):
    objects = CachedManager()


class Feed(BaseModel):
    name = models.TextField()
    url = models.URLField(unique=True)
    source = models.ForeignKey(NewsSource, on_delete=models.CASCADE)
    is_top_news = models.BooleanField()
    is_archive = models.BooleanField(default=False)

    objects = CachedManager()

    def __str__(self):
        return '%s:%s' % (self.source, self.name)

    def crawl_feed(self):
        if self.is_archive:
            _LOG.warning('cant crawl archive feed')
            return

        d = feedparser.parse(self.url)
        for entry in d['entries']:
            url = entry.pop('link')
            published_on = entry.pop('published_parsed')
            if isinstance(published_on, struct_time):
                published_on = datetime.fromtimestamp(mktime(published_on))
            try:
                a = Article.objects.create(feed=self,
                                           url=url,
                                           title=entry.pop('title'),
                                           summary=entry.pop('summary', None),
                                           published_on=published_on,
                                           is_top_news=self.is_top_news,
                                           metadata=entry)
            except IntegrityError as ex:
                if 'duplicate key value violates unique constraint' in ex.args[0]:
                    _LOG.info('Article with url:[%s] exists', url)
                else:
                    raise ex
            else:
                _LOG.info('Article created with url:[%s]', url)
                a.process_async()

    def crawl_feed_async(self):
        from mnemonic.news.tasks import crawl_feed_async
        crawl_feed_async.apply_async(kwargs={'feed_id': self.pk},
                                     queue=settings.CELERY_TASK_QUEUE_CRAWL_FEED,
                                     routing_key=settings.CELERY_TASK_ROUTING_KEY_CRAWL_FEED)


class Article(BaseModel, NewsIndexable):
    INDEX_NEWS_TYPE_FIELD = 'news_type'
    INDEX_SOURCE_FIELD = 'feed.source.name'
    INDEX_SOURCE_TYPE_FIELD = 'feed.source.__class__.__name__'
    INDEX_TITLE_FIELD = 'title'
    INDEX_BODY_FIELD = 'body'
    INDEX_PUBLISHED_ON_FIELD = 'published_on'
    INDEX_URL_FIELD = 'url'

    feed = models.ForeignKey(Feed, on_delete=models.CASCADE)
    url = models.URLField(unique=True, max_length=2048)
    title = models.TextField()
    summary = models.TextField(blank=True, null=True)
    body = models.TextField(blank=True, null=True)
    published_on = models.DateField(blank=True, null=True)
    is_top_news = models.BooleanField(default=False)
    metadata = JSONField()
    is_pushed_to_index = models.BooleanField(default=False)

    def __str__(self):
        return '%s:%s' % (self.feed, self.title)

    @property
    def news_type(self):
        return 'news'

    def save(self, *args, **kwargs):
        if self.feed.source == 'Google News India':
            parsed = urlparse.urlparse(self.url)
            if parsed.netloc == 'news.google.com':
                self.url = urlparse.parse_qs(parsed.query)['url'][0]
        super(Article, self).save(*args, **kwargs)

    def process(self):
        from mnemonic.news.utils.article_utils import get_body_from_article

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
        from mnemonic.news.tasks import process_article_async
        process_article_async.apply_async(kwargs={'article_id': self.pk},
                                          queue=settings.CELERY_TASK_QUEUE_PROCESS_ARTICLE,
                                          routing_key=settings.CELERY_TASK_ROUTING_KEY_PROCESS_ARTICLE)


class TwitterUser(object):
    def __init__(self, name):
        self.name = name


class Tweet(BaseModel, NewsIndexable):
    INDEX_NEWS_TYPE_FIELD = 'news_type'
    INDEX_SOURCE_FIELD = 'entity_proxy.name'
    INDEX_SOURCE_TYPE_FIELD = 'entity_proxy.__class__.__name__'
    INDEX_MENTIONS_FIELD = 'mentions'
    INDEX_TITLE_FIELD = 'tweet'
    INDEX_PUBLISHED_ON_FIELD = 'published_on'
    INDEX_URL_FIELD = 'url'

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    entity = GenericForeignKey('content_type', 'object_id')
    tweet_id = models.BigIntegerField(unique=True)
    tweet = models.TextField()
    published_on = models.DateTimeField()
    metadata = JSONField()
    is_pushed_to_index = models.BooleanField(default=False)

    @cached_property
    def entity_proxy(self):
        if self.object_id is not None and self.content_type_id is not None:
            return self.content_type.model_class().objects.get(pk=self.object_id)
        else:
            return TwitterUser(self.metadata.get('name'))

    @cached_property
    def mentions(self):
        return [d['name'] for d in self.metadata.get('reply_to', [])]

    def __str__(self):
        return '%s: %s' % (self.entity, self.tweet)

    @property
    def news_type(self):
        return 'tweet'

    @property
    def url(self):
        return self.metadata['link']

    def process(self):
        if not self.is_pushed_to_index:
            self.push_to_index()
            self.is_pushed_to_index = True
            self.save(update_fields=['is_pushed_to_index'])
            _LOG.info('processed tweet:[%s][%s]', self.pk, self.tweet_id)

    def process_async(self):
        from mnemonic.news.tasks import process_tweet_async
        process_tweet_async.apply_async(kwargs={'tweet_id': self.pk},
                                          queue=settings.CELERY_TASK_QUEUE_PROCESS_TWEET,
                                          routing_key=settings.CELERY_TASK_ROUTING_KEY_PROCESS_TWEET)
