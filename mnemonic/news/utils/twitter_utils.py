import msgpack
from retry import retry
import twint
from twint.tweet import tweet as Tweet
from twint.token import TokenExpiryException

from mnemonic.news.utils.string_utils import slugify


def get_crawl_fname(prefix, signature_parts):
    s = slugify('_'.join(signature_parts), retain_punct={'@'})
    return prefix % s


class CrawlBuffer(object):
    def __init__(self, signature_parts):
        self.fname = get_crawl_fname('state/twint/results_%s.csv', signature_parts)
        self.file = open(self.fname, 'a')

    def append(self, tweet):
        self.file.write(msgpack.packb(vars(tweet), use_bin_type=True))

    def get_data(self):
        self.file.flush()
        self.file.close()
        data = msgpack.Unpacker(open(self.fname), raw=False)
        for d in data:
            t = Tweet()
            t.__dict__.update(d)
            yield t


@retry(tries=1000)
def get_tweets_for_username(username, limit=None, since=None, until=None, mentions=False, language=None):
    c = twint.Config()
    if mentions:
        c.Search = '@' + username
        signature_parts = [c.Search]
    else:
        c.Username = username
        signature_parts = [c.Username]

    if limit:
        c.Limit = limit

    if since:
        c.Since = since.strftime('%Y-%m-%d %H:%M:%S')
        signature_parts.append(c.Since)

    if until:
        c.Until = until.strftime('%Y-%m-%d %H:%M:%S')
        signature_parts.append(c.Until)

    if language:
        c.Lang = language

    c.Store_object = True
    c.Store_object_tweets_list = CrawlBuffer(signature_parts)
    c.Resume = get_crawl_fname('state/twint/resume_%s.txt', signature_parts)
    twint.run.Search(c)
    return c.Store_object_tweets_list.get_data()
