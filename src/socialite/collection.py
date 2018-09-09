from enum import Enum
from uuid import uuid4
from uuid import UUID

import daiquiri

from socialite import fdb
from socialite.base import SocialiteException
from socialite.base import SubspacePrefix
from socialite.base import dumps
from socialite.base import loads


log = daiquiri.getLogger(__name__)


class Collection(Enum):
    USERS = b'\x00'
    STREAM = b'\x01'
    FOLLOWING = b'\x02'


class CollectionSpace(Enum):
    METADATA = b'\x00'
    DATA = b'\x01'


@fdb.transactional
async def _random_identifier(tr, prefix):
    """Look for a random key that has no value"""
    # TODO: maybe remove the for loop
    for _ in range(255):
        uid = uuid4()
        key = prefix + uid.bytes
        value = await tr.get(key)
        if value == b'':
            return uid
    msg = 'It seems like the collection is full!'
    raise SocialiteException(msg)


@fdb.transactional
async def all(tr, collection):
    prefix = SubspacePrefix.COLLECTIONS.value + collection.value + CollectionSpace.DATA.value
    start = prefix
    end = fdb.strinc(prefix)
    out = []
    msg = "fetching everything in collection=%r between start=%r and end=%r"
    log.debug(msg, collection.name, start, end)
    items = tr.get_range(start, end)
    async for key, value in items:
        uid = key[len(prefix):]
        uid = UUID(bytes=uid)
        document = loads(value)
        document['uid'] = uid
        out.append(document)
    return out


@fdb.transactional
async def insert(tr, collection, **document):
    prefix = SubspacePrefix.COLLECTIONS.value + collection.value + CollectionSpace.DATA.value
    uid = await _random_identifier(tr, prefix)
    key = prefix + uid.bytes
    value = dumps(document)
    tr.set(key, value)
    return uid


@fdb.transactional
async def update(tr, collection, uid, **document):
    prefix = SubspacePrefix.COLLECTIONS.value + collection.value + CollectionSpace.DATA.value
    key = prefix + uid.bytes
    value = dumps(document)
    tr.set(key, value)


@fdb.transactional
async def get(tr, collection, uid):
    prefix = SubspacePrefix.COLLECTIONS.value + collection.value + CollectionSpace.DATA.value
    key = prefix + uid.bytes
    value = await tr.get(key)
    document = loads(value)
    document['uid'] = uid
    return document


@fdb.transactional
async def query(tr, collection, **where):
    documents = await all(tr, collection)
    out = []
    for document in documents:
        for key, value in where.items():
            if document.get(key) != value:
                break
        else:
            out.append(document)
    return out


@fdb.transactional
async def delete(tr, collection, uid):
    prefix = SubspacePrefix.COLLECTIONS + collection + CollectionSpace.DATA
    key = prefix + uid.bytes
    del tr[key]
