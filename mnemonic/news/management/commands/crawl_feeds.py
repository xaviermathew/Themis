from django.core.management.base import BaseCommand

from mnemonic.news.models import Feed


class Command(BaseCommand):
    def handle(self, *args, **options):
        for feed in Feed.objects.all():
            feed.crawl_feed()
