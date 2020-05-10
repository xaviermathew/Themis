from django.contrib import admin, messages

from themis.entity.models import Person, Organization, Relationship, RelationshipType, OrganizationType
from themis.core.admin import BaseAdmin


@admin.register(Person)
class PersonAdmin(BaseAdmin):
    list_display = ['name']
    actions = ['crawl_tweets']

    def crawl_tweets(self, request, qs):
        messages.add_message(request, messages.INFO, 'Twitter crawl for [%s] handles(s) has been queued' % len(qs))
        for person in qs:
            person.crawl_tweets_async()


@admin.register(OrganizationType)
class OrganizationTypeAdmin(BaseAdmin):
    list_display = ['name']


@admin.register(Organization)
class OrganizationAdmin(BaseAdmin):
    list_display = ['name']


@admin.register(RelationshipType)
class RelationshipTypeAdmin(BaseAdmin):
    list_display = ['name']


@admin.register(Relationship)
class RelationshipAdmin(BaseAdmin):
    list_display = ['from_entity', 'type', 'to_entity']
    list_filter = ['type']
