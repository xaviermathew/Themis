from newspaper import Article as NArticle

from mnemonic.news.utils.cache_utils import DownloadCache


def get_body_from_html(url, html, cache=False):
    if cache:
        dc = DownloadCache(url)
        if not dc.is_cached():
            dc.cache(html)

    narticle = NArticle(url, fetch_images=False)
    narticle.set_html(html)
    narticle.parse()
    return narticle.text


def get_body_from_article(url):
    html = DownloadCache(url).get()
    return get_body_from_html(url, html)
