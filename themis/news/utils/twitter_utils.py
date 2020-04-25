import twint


def get_tweets_for_username(username, limit=100):
    c = twint.Config()

    c.Username = username
    c.Limit = limit
    c.Store_object = True
    c.User_full = True

    twint.run.Search(c)
    return twint.output.tweets_list
