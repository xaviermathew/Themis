import string

PUNCT = set(string.punctuation)
PUNCT.add(' ')


def slugify(s, joiner='_'):
    result = []
    for c in s.lower():
        if c in PUNCT:
            result.append(joiner)
        else:
            result.append(c)
    return joiner.join(filter(bool, ''.join(result).split(joiner)))


def clean(s):
    s1 = ''.join([c if ord(c) < 128 else ' ' for c in s])
    return ' '.join(s1.split())
