from enum import Enum
import msgpack


class SocialiteException(Exception):
    """Base socialite exception"""
    pass


class SocialiteBase:
    """Base class for all socialite class"""
    pass


class SubspacePrefix(Enum):
    COLLECTIONS = b'\x00'


def dumps(o):
    return msgpack.dumps(o, encoding='utf-8')


def loads(bytes):
    return msgpack.loads(bytes, encoding='utf-8')
