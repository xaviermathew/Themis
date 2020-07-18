import copy
from datetime import datetime

from django.conf import settings

from mnemonic.contrib.article_archive_scrapers.base.spider import BaseArchiveSpider
from mnemonic.news.utils.string_utils import clean


class ArchiveSpider(BaseArchiveSpider):
    name = 'indian_express'
    feed_url = 'https://archive.indianexpress.com/'
    news_source_name = 'Indian Express Archive'
    article_domain = 'archive.indianexpress.com'

    def get_feed_name(self, item, body):
        return item['metadata']['section']

    def parse(self, response):
        yield from self.parse_archive_index(response)

    def parse_archive_index(self, response):
        for day in response.xpath('//*[@id="box_left"]/div/table/tbody/tr/td/div/div/table/tr/td/a'):
            day_url = day.attrib.get('href')
            if day_url and '/old/' not in day_url:
                parts = list(map(int, day_url.strip('/').split('/')[-3:]))
                meta = copy.deepcopy(response.meta)
                meta['article']['published_on'] = datetime(year=parts[2], month=parts[1], day=parts[0])
                yield response.follow(url=day_url, callback=self.parse_day_index, meta=meta)
                if settings.SHOULD_LIMIT_ARCHIVE_CRAWL:
                    break

    def parse_day_index(self, response):
        for section in response.xpath('//*[@id="box_left"]/div/div[*]'):
            section_title = section.xpath('h4/text()').get().strip()
            for article in section.xpath('div/ul/li'):
                meta = copy.deepcopy(response.meta)
                meta['article']['metadata'] = {'section': clean(section_title)}
                meta['article']['title'] = article.xpath('text()').get().strip()
                url = article.xpath('a/@href').get()
                yield from self.crawl_article(response, url, meta=meta)
                if settings.SHOULD_LIMIT_ARCHIVE_CRAWL:
                    break
