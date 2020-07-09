import twint


def get_tweets_for_username(username, limit=None):
    c = twint.Config()
    c.Username = username
    if limit:
        c.Limit = limit
    else:
        c.User_full = True
    c.Store_object = True
    twint.run.Search(c)
    return twint.output.tweets_list
