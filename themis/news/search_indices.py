from elasticsearch_dsl import Document, Keyword, Text
from elasticsearch_dsl.connections import connections

connections.create_connection(hosts=['localhost'])


class News(Document):
    author = Text(analyzer='snowball', fields={'raw': Keyword()})
    title = Text(analyzer='snowball', fields={'raw': Keyword()})
    body = Text(analyzer='snowball')
    class Index:
        name = 'news'


# News.init()


class NewsIndexable(object):
    NEWS_AUTHOR_FIELD = None
    NEWS_TITLE_FIELD = None
    NEWS_BODY_FIELD = None

    def get_index_meta_data(self):
        return {'uid': self.get_uid()}

    def get_index_data(self):
        d = {}
        if self.NEWS_AUTHOR_FIELD:
            d['author'] = getattr(self, self.NEWS_AUTHOR_FIELD)
        if self.NEWS_TITLE_FIELD:
            d['title'] = getattr(self, self.NEWS_TITLE_FIELD)
        if self.NEWS_BODY_FIELD:
            d['body'] = getattr(self, self.NEWS_BODY_FIELD)
        return d

    def index(self):
        news = News(meta=self.get_index_meta_data(), **self.get_index_data())
        news.save()
