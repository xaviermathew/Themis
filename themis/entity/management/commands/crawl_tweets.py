from django.conf import settings
from django.core.management.base import BaseCommand

from themis.entity.models import Person


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('--limit', default=settings.TWITTER_CRAWL_LIMIT, type=int,
                            help="How many tweets to crawl")

    def handle(self, *args, **options):
        for person in Person.objects.all():
            person.crawl_tweets_async(limit=options['limit'])
