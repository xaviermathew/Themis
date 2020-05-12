from django.core.management.base import BaseCommand

from themis.entity.models import Person


class Command(BaseCommand):
    def handle(self, *args, **options):
        for person in Person.objects.all():
            person.crawl_tweets_async()
