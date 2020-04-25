from __future__ import unicode_literals

from datetime import datetime
import logging

import pytz
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models, IntegrityError

from themis.models import BaseModel

_LOG = logging.getLogger(__name__)


class EntityBase(BaseModel):
    name = models.TextField()

    class Meta:
        abstract = True

    def __str__(self):
        return self.name

    @staticmethod
    def get_entity_types():
        return EntityBase.__subclasses__()


class OrganizationType(EntityBase):
    pass


class Organization(EntityBase):
    type = models.ForeignKey(OrganizationType, on_delete=models.CASCADE)

    def __str__(self):
        return '%s:%s' % (self.type, self.name)


class Person(EntityBase):
    twitter_handle = models.CharField(max_length=256)

    def crawl_tweets(self):
        from news.models import Tweet
        from news.utils.twitter_utils import get_tweets_for_username

        if self.twitter_handle is None:
            _LOG.warning('%s does not have a twitter handle', self)
            return

        tweets = get_tweets_for_username(self.twitter_handle)
        non_metadata_keys = {'id', 'id_str', 'tweet', 'datetime', 'datestamp', 'timestamp'}
        for tweet in tweets:
            published_on = datetime.fromtimestamp(tweet.datetime / 1000, pytz.utc)
            metadata = {k: v for k, v in vars(tweet).items() if k not in non_metadata_keys}
            try:
                t = Tweet.objects.create(person=self,
                                         tweet_id=tweet.id,
                                         tweet=tweet.tweet,
                                         published_on=published_on,
                                         metadata=metadata)
            except IntegrityError as ex:
                _LOG.info('Tweet with id:[%s] may already exist - %s', tweet.id, ex)
            else:
                _LOG.info('Tweet created with id:[%s]', tweet.id)
                t.process_async()

    def crawl_tweets_async(self):
        from entity.tasks import crawl_tweets_async
        crawl_tweets_async.apply_async(kwargs={'person_id': self.pk},
                                       queue=settings.CELERY_TASK_QUEUE_CRAWL_TWITTER,
                                       routing_key=settings.CELERY_TASK_ROUTING_KEY_CRAWL_TWITTER)


class RelationshipType(EntityBase):
    pass


class Relationship(BaseModel):
    from_entity_content_type = models.ForeignKey(ContentType,
                                                 on_delete=models.CASCADE,
                                                 related_name='from_entity_content_type')
    from_entity_object_id = models.PositiveIntegerField()
    from_entity = GenericForeignKey('from_entity_content_type', 'from_entity_object_id')

    to_entity_content_type = models.ForeignKey(ContentType,
                                               on_delete=models.CASCADE,
                                               related_name='to_entity_content_type')
    to_entity_object_id = models.PositiveIntegerField()
    to_entity = GenericForeignKey('to_entity_content_type', 'to_entity_object_id')

    type = models.ForeignKey(RelationshipType, on_delete=models.CASCADE)

    def __str__(self):
        return '[%s]-(%s)->[%s]' % (self.from_entity, self.type, self.to_entity)
