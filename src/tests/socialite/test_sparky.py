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
    patterns = [
        ('blog', sparky.var('blog'), 'title', 'sparky'),
        ('post', sparky.var('post'), 'blog', sparky.var('blog')),
        ('post', sparky.var('post'), 'title', sparky.var('title')),
    ]
    out = await sparky.where(db, *patterns)
    out = [dict(x.items()) for x in out]
    assert out == [{'blog': 'uid1', 'post': 'uid3', 'title': 'sparky query language'}]


@pytest.mark.asyncio
async def test_stuff():
    db = await open()
    tuples = [
        # abki
        ('actor', '74c69c2adfef4648b286b720c69a334b', 'is a', 'user'),
        ('actor', '74c69c2adfef4648b286b720c69a334b', 'name', 'abki'),
        # amz31
        ('actor', 'f1e18a79a9564018b2cccef24911e931', 'is a', 'user'),
        ('actor', 'f1e18a79a9564018b2cccef24911e931', 'name', 'amz31'),
        # abki says poor man social network
        ('stream', '78ad80d0cb7e4975acb1f222c960901d', 'created-at', 1536859544),
        ('stream', '78ad80d0cb7e4975acb1f222c960901d', 'expression', 'poor man social network'),
        ('stream', '78ad80d0cb7e4975acb1f222c960901d', 'html', '<p>poor man social network</p>\n'),
        ('stream', '78ad80d0cb7e4975acb1f222c960901d', 'modified-at', 1536859544),
        ('stream', '78ad80d0cb7e4975acb1f222c960901d', 'actor', '74c69c2adfef4648b286b720c69a334b'),
        # amz31 follow abki
        ('stream', 'd563fd7cdbd84c449d36f1e6cf5893a3', 'followee', '74c69c2adfef4648b286b720c69a334b'),  # noqa
        ('stream', 'd563fd7cdbd84c449d36f1e6cf5893a3', 'follower', 'f1e18a79a9564018b2cccef24911e931'),  # noqa
        # abki says socialite for the win
        ('stream', 'fe066559ce894d9caf2bca63c42d98a8', 'created-at', 1536859522),
        ('stream', 'fe066559ce894d9caf2bca63c42d98a8', 'expression', 'socialite for the win!'),
        ('stream', 'fe066559ce894d9caf2bca63c42d98a8', 'html', '<p>socialite for the win!</p>\n'),
        ('stream', 'fe066559ce894d9caf2bca63c42d98a8', 'modified-at', 1536859522),
        ('stream', 'fe066559ce894d9caf2bca63c42d98a8', 'actor', '74c69c2adfef4648b286b720c69a334b')
    ]
    await sparky.add(db, *tuples)
    everything = await sparky.all(db)
    assert len(everything) == len(tuples)

    user = 'f1e18a79a9564018b2cccef24911e931'
    patterns = (
        ('stream', sparky.var('follow'), 'follower', user),
        ('stream', sparky.var('follow'), 'followee', sparky.var('followee')),
        ('stream', sparky.var('expression'), 'html', sparky.var('html')),
        ('stream', sparky.var('expression'), 'actor', sparky.var('followee')),
        ('stream', sparky.var('expression'), 'modified-at', sparky.var('modified-at')),
        ('actor', sparky.var('followee'), 'name', sparky.var('name')),
    )
    out = await sparky.where(db, *patterns)
    out.sort(key=lambda x: x['modified-at'], reverse=True)
    assert len(out) == 2
    assert [b['expression'] for b in out] == ['78ad80d0cb7e4975acb1f222c960901d', 'fe066559ce894d9caf2bca63c42d98a8']  # noqa
