from datetime import datetime, timedelta

import twint


def get_tweets_for_username(username, limit=None, since_hours=None, mentions=False, language=None):
    c = twint.Config()
    if mentions:
        c.Search = '@' + username
    else:
        c.Username = username
    if limit:
        c.Limit = limit
    if since_hours:
        since = datetime.today() - timedelta(hours=since_hours)
        c.Since = since.strftime('%Y-%m-%d %H:%M:%S')
    if language:
        c.Lang = language
    c.Store_object = True
    twint.run.Search(c)
    return twint.output.tweets_list
