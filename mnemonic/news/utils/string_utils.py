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
