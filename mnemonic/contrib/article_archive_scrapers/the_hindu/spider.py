import copy
from datetime import datetime

import scrapy
from django.conf import settings

from mnemonic.contrib.article_archive_scrapers.base.spider import BaseArchiveSpider


class ArchiveSpider(BaseArchiveSpider):
    name = 'the_hindu'
    feed_url = 'https://www.thehindu.com/archive'
    news_source_name = 'The Hindu Archive'

    def get_feed_name(self, item, body):
        return item['metadata']['section']

    def parse(self, response):
        yield from self.parse_archive_index(response)

    def parse_archive_index(self, response):
        for month in response.xpath('//*[@id="archiveWebContainer" or @id="archiveTodayContainer"]/div[2]/ul/li/a'):
            month_url = month.attrib.get('href')
            if month_url and self.is_url_valid(url=month_url, response=response):
                yield response.follow(url=month_url, callback=self.parse_month_index, meta=response.meta)
                if settings.SHOULD_LIMIT_ARCHIVE_CRAWL:
                    break

    def parse_month_index(self, response):
        for day in response.xpath('//*[@id="archiveDayDatePicker"]/table/tbody/tr/td/a'):
            day_url = day.attrib.get('href')
            if day_url:
                parts = list(map(int, day_url.strip('/').split('/')[-3:]))
                meta = copy.deepcopy(response.meta)
                meta['article']['published_on'] = datetime(year=parts[0], month=parts[1], day=parts[2])
                if self.is_url_valid(url=day_url, response=response):
                    yield response.follow(url=day_url, callback=self.parse_day_index, meta=meta)
                    if settings.SHOULD_LIMIT_ARCHIVE_CRAWL:
                        break

    def parse_day_index(self, response):
        for section in response.xpath('/html/body/div[2]/section[1]/div/div/div/div/section'):
            section_title = section.xpath('div[1]/div/h2/a/text()').get().strip()
            for article in section.xpath('div[2]/div/div/div/ul/li/a'):
                meta = copy.deepcopy(response.meta)
                meta['article']['metadata'] = {'section': section_title}
                meta['article']['title'] = article.xpath('text()').get().strip()
                url = article.attrib['href']
                if self.is_url_valid(url=url, response=response):
                    yield self.crawl_article(response, url, meta=meta)
                    if settings.SHOULD_LIMIT_ARCHIVE_CRAWL:
                        break
