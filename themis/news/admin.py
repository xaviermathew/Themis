from django.contrib import admin, messages

from themis.core.admin import BaseAdmin
from themis.news.models import Article, Feed, NewsSource, Tweet


@admin.register(Article)
class ArticleAdmin(BaseAdmin):
    list_display = ['feed', 'title', 'published_on']
    list_filter = ['feed__source', 'is_top_news', 'is_pushed_to_index']


@admin.register(NewsSource)
class NewsSourceAdmin(BaseAdmin):
    list_display = ['name']


@admin.register(Feed)
class FeedAdmin(BaseAdmin):
    list_display = ['name', 'source', 'is_top_news']
    list_filter = ['source', 'is_top_news']
    actions = ['crawl_feed']

    def crawl_feed(self, request, qs):
        messages.add_message(request, messages.INFO, 'Crawl for [%s] feed(s) has been queued' % len(qs))
        for feed in qs:
            feed.crawl_feed_async()


@admin.register(Tweet)
class TweetAdmin(BaseAdmin):
    list_display = ['entity', 'tweet', 'published_on']
    list_filter = ['entity', 'published_on']
