from urllib.parse import urlparse

import scrapy
from scrapy.utils.project import get_project_settings
from urlnormalizer import normalize_url

from django.conf import settings
from django.db.models import Q

from mnemonic.contrib.article_archive_scrapers.base.items import ArticleItemPipeline, ArticleItem
from mnemonic.news.models import Feed, NewsSource, Article
from mnemonic.news.utils.cache_utils import DownloadCacheStorage
from mnemonic.news.utils.class_utils import get_python_path
from mnemonic.news.utils.string_utils import slugify


class BaseArchiveSpider(scrapy.Spider):
    name = None
    feed_name = None
    feed_url = None
    feed_is_top_news = False
    news_source_name = None
    article_domain = None

    @staticmethod
    def get_settings():
        d = get_project_settings()
        d['LOG_LEVEL'] = 'INFO'
        d['ITEM_PIPELINES'] = {get_python_path(ArticleItemPipeline): 100}
        d['DOWNLOADER_MIDDLEWARES'] = {'scrapy.downloadermiddlewares.httpcache.HttpCacheMiddleware': 100}
        d['HTTPCACHE_ENABLED'] = True
        d['HTTPCACHE_STORAGE'] = get_python_path(DownloadCacheStorage)
        d['HTTPCACHE_DIR'] = settings.ARTICLE_ARCHIVE_CACHE_DIR
        return d

    @classmethod
    def get_news_source(cls):
        try:
            return NewsSource.objects.get_cached(name=cls.news_source_name)
        except NewsSource.DoesNotExist:
            return NewsSource.objects.create(name=cls.news_source_name)

    def is_top_news(self, item, body):
        return True

    def get_feed_name(self, item, body):
        return self.feed_name

    def get_feed(self, item, body):
        feed_name = self.get_feed_name(item, body).title()
        feed_hash = slugify(feed_name)
        feed_url = '%s#%s' % (self.feed_url, feed_hash)
        try:
            return Feed.objects.get_cached(url=feed_url)
        except Feed.DoesNotExist:
            source = self.get_news_source()
            return Feed.objects.create(
                name=feed_name,
                url=feed_url,
                source=source,
                is_archive=True,
                is_top_news=self.feed_is_top_news
            )

    def start_requests(self):
        yield scrapy.Request(url=self.feed_url, callback=self.parse, meta={'article': {}})

    def parse(self, response):
        raise NotImplementedError

    @staticmethod
    def _split_url(response, url):
        full_url = normalize_url(response.urljoin(url))
        return urlparse(full_url)

    def is_url_valid(self, url_parts=None, url=None, response=None):
        if url_parts is None:
            url_parts = self._split_url(response, url)
        article_domain = self.article_domain
        if article_domain is not None and url_parts.netloc != article_domain:
            return False
        return True

    def crawl_article(self, response, url, meta, callback=None):
        url_parts = self._split_url(response, url)
        url_checks = Q(url=url_parts._replace(scheme='http').geturl()) | \
                     Q(url=url_parts._replace(scheme='https').geturl())

        if not self.is_url_valid(url_parts):
            self.log('Article with url:[%s] does not match domain:[%s]' % (url, self.article_domain))
        elif Article.objects.filter(url_checks).exists():
            self.log('Article with url:[%s] exists' % url)
        else:
            if callback is None:
                callback = self.parse_article
            return response.follow(url, callback=callback, meta=meta)

    def parse_article(self, response):
        yield ArticleItem(
            url=response.url,
            html=response.body,
            **response.meta['article']
        )
