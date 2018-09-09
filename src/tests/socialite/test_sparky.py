import asyncio
import pytest

from found.v510 import base

from socialite import fdb
from socialite import sparky


async def open():
    # XXX: hack around the fact that the loop is cached in found
    loop = asyncio.get_event_loop()
    base._loop = loop

    db = await fdb.open()
    # clean database
    tr = db._create_transaction()
    tr.clear_range(b'\x00', b'\xff')
    await tr.commit()

    return db


@pytest.mark.asyncio
async def test_empty():
    db = await open()
    tuples = await sparky.all(db)
    assert tuples == []


@pytest.mark.asyncio
async def test_one_tuple():
    db = await open()
    expected = (1, 2, 3, 4)
    await sparky.add(db, expected)
    tuples = await sparky.all(db)
    assert tuples == [expected]


@pytest.mark.asyncio
async def test_many_tuples():
    db = await open()
    expected = [
        (1, 2, 3, 4),
        (1, 9, 8, 5),
        (1, 3, 3, 7),
    ]
    expected.sort()  # XXX: sparky keeps ordering
    await sparky.add(db, *expected)
    tuples = await sparky.all(db)
    assert tuples == expected


@pytest.mark.asyncio
async def test_where_one_pattern():
    db = await open()
    data = [
        ('blog', 'uid1', 'title', 'sparky'),
        ('blog', 'uid1', 'description', 'rdf / sparql for humans'),
        ('blog', 'uid2', 'title', 'hyperdev.fr'),
        ('blog', 'uid2', 'descrption', 'forward and beyond!'),
    ]
    await sparky.add(db, *data)
    out = await sparky.where(db, ('blog', 'uid1', sparky.var('key'), sparky.var('value')))
    out = [dict(x.items()) for x in out]
    assert out == [
        {'key': 'description', 'value': 'rdf / sparql for humans'},
        {'key': 'title', 'value': 'sparky'}
    ]


@pytest.mark.asyncio
async def test_where_several_pattern():
    db = await open()
    data = [
        ('blog', 'uid1', 'title', 'sparky'),
        ('blog', 'uid1', 'description', 'rdf / sparql for humans'),
        ('post', 'uid3', 'blog', 'uid1'),
        ('post', 'uid3', 'title', 'sparky query language'),
        ('blog', 'uid2', 'title', 'hyperdev.fr'),
        ('blog', 'uid2', 'descrption', 'forward and beyond!'),
    ]
    await sparky.add(db, *data)
    query = [
        ('blog', sparky.var('blog'), 'title', 'sparky'),
        ('post', sparky.var('post'), 'blog', sparky.var('blog')),
        ('post', sparky.var('post'), 'title', sparky.var('title')),
    ]
    out = await sparky.where(db, *query)
    out = [dict(x.items()) for x in out]
    assert out == [{'blog': 'uid1', 'post': 'uid3', 'title': 'sparky query language'}]
