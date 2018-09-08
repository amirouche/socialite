import asyncio
import pytest

from found.v510 import base

from socialite import fdb
from socialite import collection


USERS = collection.Collection.USERS


async def open():
    # XXX: hack around the fact that the loop is cached in found
    loop = asyncio.get_event_loop()
    base._loop = loop

    db = await fdb.open()
    # clean database
    tr = db._create_transaction()
    tr.clear_range(b'', b'\xff')
    await tr.commit()

    return db


@pytest.mark.asyncio
async def test_empty_collection():
    db = await open()
    documents = await collection.all(db, USERS)
    assert documents == []


@pytest.mark.asyncio
async def test_collection():
    db = await open()
    uid = await collection.insert(db, USERS, username='amz3')
    documents = await collection.all(db, USERS)
    assert len(documents) == 1
    assert documents[0]['uid'] == uid
    assert documents[0]['username'] == 'amz3'


@pytest.mark.asyncio
async def test_query_single_term():
    db = await open()
    await collection.insert(db, USERS, username='amz3', score=42)
    await collection.insert(db, USERS, username='amirouche', score=0)
    await collection.insert(db, USERS, username='abki', score=0)
    documents = await collection.query(db, USERS, score=0)
    assert len(documents) == 2
    out = set([document['username'] for document in documents])
    expected = set(['amirouche', 'abki'])
    assert out == expected


@pytest.mark.asyncio
async def test_query_two_terms():
    db = await open()
    await collection.insert(db, USERS, username='amz3', score=42)
    uid = await collection.insert(db, USERS, username='amirouche', score=0)
    await collection.insert(db, USERS, username='abki', score=0)
    documents = await collection.query(db, USERS, username='amirouche', score=0)
    assert len(documents) == 1
    assert documents[0]['uid'] == uid
