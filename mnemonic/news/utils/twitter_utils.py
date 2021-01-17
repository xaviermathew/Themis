from retry import retry
import twint
from twint.token import TokenExpiryException

from mnemonic.news.utils.string_utils import slugify


@retry((TokenExpiryException, AttributeError), tries=1000)
def get_tweets_for_username(username, limit=None, since=None, until=None, mentions=False, language=None):
    c = twint.Config()
    if mentions:
        c.Search = '@' + username
        resume_signature_parts = [c.Search]
    else:
        c.Username = username
        resume_signature_parts = [c.Username]

    if limit:
        c.Limit = limit

    if since:
        c.Since = since.strftime('%Y-%m-%d %H:%M:%S')
        resume_signature_parts.append(c.Since)

    if until:
        c.Until = until.strftime('%Y-%m-%d %H:%M:%S')
        resume_signature_parts.append(c.Until)

    if language:
        c.Lang = language

    c.Store_object = True
    c.Resume = 'state/twint/%s' % slugify('_'.join(resume_signature_parts), retain_punct={'@'})
    twint.run.Search(c)
    return twint.output.tweets_list
