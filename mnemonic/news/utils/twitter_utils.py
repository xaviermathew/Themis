import twint


def get_tweets_for_username(username, limit=None):
    c = twint.Config()

    c.Username = username
    if limit:
        c.Limit = limit
    c.Store_object = True
    c.User_full = True

    twint.run.Search(c)
    return twint.output.tweets_list
