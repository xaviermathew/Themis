import string

from django.core.validators import EMPTY_VALUES

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


def get(obj, path, raise_errors=False):
    if obj in EMPTY_VALUES:
        return

    if not path:
        if raise_errors:
            raise ValueError("path can't be empty")
        else:
            return

    if path.count('.') >= 1:
        k, path_pending = path.split('.', 1)
    else:
        k = path
        path_pending = ''

    try:
        if isinstance(obj, dict):
            value = obj[k]
        else:
            value = getattr(obj, k)
    except (KeyError, AttributeError):
        if raise_errors:
            raise ValueError('path:[%s] not available on obj:[%s]' % (path, obj))
        else:
            return

    if len(path_pending) > 1:
        value = get(value, path_pending, raise_errors)
    return value
