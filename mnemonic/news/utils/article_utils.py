from newspaper import Article as NArticle

from mnemonic.news.utils.cache_utils import DownloadCache


def get_body_from_article(url):
    narticle = NArticle(url)
    html = DownloadCache(url).get()
    narticle.set_html(html)
    narticle.parse()
    return narticle.text
