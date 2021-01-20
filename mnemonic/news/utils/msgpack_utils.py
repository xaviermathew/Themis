import datetime

from kombu.serialization import register
import msgpack


def decode_datetime(obj):
    if b'__datetime__' in obj:
        obj = datetime.datetime.strptime(obj[b'as_str'].decode(), "%Y%m%dT%H:%M:%S.%f")
    return obj


def encode_datetime(obj):
    if isinstance(obj, datetime.datetime):
        obj = {'__datetime__': True, 'as_str': obj.strftime("%Y%m%dT%H:%M:%S.%f").encode()}
    return obj


def dumps(obj, **kwargs):
    return msgpack.packb(obj, default=encode_datetime, **kwargs)


def loads(stream, **kwargs):
    return msgpack.Unpacker(stream, raw=False, object_hook=decode_datetime, **kwargs)


register('mmsgpack', dumps, loads, content_type='application/x-mmsgpack', content_encoding='utf-8')
