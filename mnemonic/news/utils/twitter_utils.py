import datetime

import msgpack
from retry import retry
import twint
from twint.tweet import tweet as Tweet
from twint.token import TokenExpiryException

from mnemonic.news.utils.string_utils import slugify


def decode_datetime(obj):
    if b'__datetime__' in obj:
        obj = datetime.datetime.strptime(obj[b'as_str'].decode(), "%Y%m%dT%H:%M:%S.%f")
    return obj


def encode_datetime(obj):
    if isinstance(obj, datetime.datetime):
        obj = {'__datetime__': True, 'as_str': obj.strftime("%Y%m%dT%H:%M:%S.%f").encode()}
    return obj


def get_crawl_fname(prefix, signature_parts):
    s = slugify('_'.join(signature_parts), retain_punct={'@'})
    return prefix % s


class CrawlBuffer(object):
    def __init__(self, signature_parts):
        self.fname = get_crawl_fname('state/twint/results_%s.msgpack', signature_parts)
        self.file = open(self.fname, 'ab')

    def append(self, tweet):
        self.file.write(msgpack.packb(vars(tweet), use_bin_type=True, default=encode_datetime))

    def get_data(self):
        self.file.flush()
        self.file.close()
        data = msgpack.Unpacker(open(self.fname, 'rb'), raw=False, object_hook=decode_datetime)
        for d in data:
            t = Tweet()
            t.__dict__.update(d)
            yield t


@retry(tries=1000)
def get_tweets_for_username(username, limit=None, since=None, until=None, mentions=False, language=None, only_cached=False):
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
    if not only_cached:
        twint.run.Search(c)
    return c.Store_object_tweets_list.get_data()
