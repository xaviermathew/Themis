from calendar import monthrange
import copy
from datetime import date
from urllib.parse import urlparse

from django.conf import settings

from mnemonic.contrib.article_archive_scrapers.base.spider import BaseArchiveSpider

START_TIME = date(year=1899, month=12, day=30)


def get_section_from_url(url):
    stop_idx = None
    parts = urlparse(url).path.split('/')
    for i, part in enumerate(parts):
        if '-' in part:
            stop_idx = i
            break
    if stop_idx is not None:
        return ' > '.join(filter(bool, parts[:stop_idx]))
    else:
        return ArchiveSpider.feed_name


class ArchiveSpider(BaseArchiveSpider):
    name = 'times_of_india'
    feed_name = 'Archive'
    feed_url = 'https://timesofindia.indiatimes.com/archive.cms'
    news_source_name = 'Times of India'
    article_domain = 'timesofindia.indiatimes.com'

    def get_feed_name(self, item, body):
        return item['metadata']['section']

    def parse(self, response):
        yield from self.parse_archive_index(response)

    def parse_archive_index(self, response):
        for month in response.xpath('//*[@id="netspidersosh"]//a[contains(@href, "/archive/year")]'):
            month_url = month.attrib.get('href')
            if month_url and self.is_url_valid(url=month_url, response=response):
                yield response.follow(url=month_url, callback=self.parse_month_index, meta=response.meta)
                if settings.SHOULD_LIMIT_ARCHIVE_CRAWL:
                    break

    def parse_month_index(self, response):
        year, month = response.url.split('/')[-1].split(',')
        year = int(year.split('-')[1])
        month = int(month.split('-')[1].split('.')[0])
        for day in monthrange(year, month):
            curr_date = date(year=year, month=month, day=day)
            day_url = '/{year}/{month}/{day}/archivelist/year-{year},month-{month},starttime-{days}.cms'.format(
                year=year, month=month, day=day, days=(curr_date - START_TIME).days
            )
            meta = copy.deepcopy(response.meta)
            meta['article']['published_on'] = curr_date
            if self.is_url_valid(url=day_url, response=response):
                yield response.follow(url=day_url, callback=self.parse_day_index, meta=meta)
                if settings.SHOULD_LIMIT_ARCHIVE_CRAWL:
                    break

    def parse_day_index(self, response):
        for article in response.xpath('/html/body/div/table/td/div/table/tr/td/span/a'):
            meta = copy.deepcopy(response.meta)
            article_url = article.attrib['href']
            meta['article']['metadata'] = {'section': get_section_from_url(article_url)}
            meta['article']['title'] = article.xpath('text()').get().strip()
            if self.is_url_valid(url=article_url, response=response):
                yield self.crawl_article(response, article_url, meta=meta)
                if settings.SHOULD_LIMIT_ARCHIVE_CRAWL:
                    break
