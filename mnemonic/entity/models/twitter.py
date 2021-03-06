from datetime import datetime
import logging
import pytz

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.db import models, IntegrityError

from .base import EntityBase

_LOG = logging.getLogger(__name__)


class TwitterMixin(EntityBase):
    twitter_handle = models.CharField(max_length=256, unique=True)

    class Meta:
        abstract = True

    def _crawl_tweets(self, limit=None, since=None, until=None, mentions=False, only_cached=False):
        from mnemonic.news.models import Tweet
        from mnemonic.news.utils.twitter_utils import get_tweets_for_username

        tweets = get_tweets_for_username(self.twitter_handle,
                                         limit=limit,
                                         since=since,
                                         until=until,
                                         language='en' if mentions else None,
                                         mentions=mentions,
                                         only_cached=only_cached)
        non_metadata_keys = {'id', 'id_str', 'tweet', 'datetime', 'datestamp', 'timestamp'}
        for tweet in tweets:
            if isinstance(tweet.datetime, int):
                published_on = datetime.fromtimestamp(tweet.datetime / 1000, pytz.utc)
            else:
                published_on = datetime.strptime(tweet.datetime, '%Y-%m-%d %H:%M:%S %Z')
            metadata = {k: v for k, v in vars(tweet).items() if k not in non_metadata_keys}
            try:
                t = Tweet.objects.create(entity=None if mentions else self,
                                         tweet_id=tweet.id,
                                         tweet=tweet.tweet,
                                         published_on=published_on,
                                         metadata=metadata)
            except IntegrityError as ex:
                if 'duplicate key value violates unique constraint' in ex.args[0]:
                    _LOG.info('Tweet with id:[%s] already exists', tweet.id)
                else:
                    raise ex
            else:
                _LOG.info('Tweet created with id:[%s]', tweet.id)
                t.process_async()

    def crawl_tweets(self, limit=None, since=None, until=None, mentions=None, only_cached=False):
        if self.twitter_handle is None:
            _LOG.warning('%s does not have a twitter handle', self)
            return

        if mentions is None:
            mentions = [False, True]
        for mentions in mentions:
            self._crawl_tweets(limit=limit, since=since, until=until, mentions=mentions, only_cached=only_cached)

    def crawl_tweets_async(self, limit=None, since=None, until=None, mentions=None):
        from mnemonic.entity.tasks import crawl_tweets_async
        crawl_tweets_async.apply_async(kwargs={'entity_ct': ContentType.objects.get_for_model(self).pk,
                                               'entity_id': self.pk,
                                               'limit': limit,
                                               'since': since,
                                               'until': until,
                                               'mentions': mentions},
                                       queue=settings.CELERY_TASK_QUEUE_CRAWL_TWITTER,
                                       routing_key=settings.CELERY_TASK_ROUTING_KEY_CRAWL_TWITTER)
