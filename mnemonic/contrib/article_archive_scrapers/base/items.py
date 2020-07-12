import logging

import scrapy
from django.db import IntegrityError
from scrapy.exceptions import DropItem

from mnemonic.news.models import Article
from mnemonic.news.utils.article_utils import get_body_from_html

_LOG = logging.getLogger(__name__)


class ArticleItem(scrapy.Item):
    url = scrapy.Field()
    html = scrapy.Field()
    metadata = scrapy.Field()
    title = scrapy.Field()
    published_on = scrapy.Field()


class ArticleItemPipeline(object):
    def process_item(self, item, spider):
        url = item['url']
        html = item.pop('html')
        body = get_body_from_html(url, html, cache=True)
        is_top_news = spider.is_top_news(item, body)
        feed = spider.get_feed(item, body)
        try:
            a = Article.objects.create(body=body,
                                       is_top_news=is_top_news,
                                       feed=feed,
                                       **item)
        except IntegrityError as ex:
            if 'duplicate key value violates unique constraint' in ex.args[0]:
                raise DropItem('Article with url:[%s] exists' % url)
            else:
                raise ex
        else:
            _LOG.info('Article created with url:[%s]', url)
            a.process_async()
