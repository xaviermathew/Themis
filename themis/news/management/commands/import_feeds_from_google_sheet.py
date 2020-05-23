import csv
import io
import logging

import requests
from django.conf import settings

from django.core.management.base import BaseCommand

from themis.news.models import Feed, NewsSource
from themis.news.utils.feed_utils import get_feed_url_from_google_sheet_id

_LOG = logging.getLogger(__name__)


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('--sheet-id', default=settings.FEED_SOURCE_GOOGLE_SHEET_ID, type=str,
                            help="Google sheets ID")

    def handle(self, *args, **options):
        sheet_url = get_feed_url_from_google_sheet_id(options['sheet_id'])
        response = requests.get(sheet_url)
        content_file = io.StringIO(response.content.decode())
        data = list(csv.DictReader(content_file))
        for d in data:
            n, n_created = NewsSource.objects.get_or_create(name=d['news_source'])
            try:
                f = Feed.objects.get(url=d['feed_url'])
            except Feed.DoesNotExist:
                Feed.objects.create(url=d['feed_url'],
                                    name=d['feed_title'],
                                    source=n,
                                    is_top_news=bool(d['is_top_news']))
                f_created = True
            else:
                f.name = d['feed_title']
                f.source = n
                f.is_top_news = bool(d['is_top_news'])
                f.save()
                f_created = False
            _LOG.info('News source:[%s][%s] feed:[%s][%s]',
                      d['news_source'], n_created, d['feed_title'], f_created)
