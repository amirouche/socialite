import asyncio
import pytest

import found
from found import base


async def open():
    # XXX: hack around the fact that the loop is cached in found
    loop = asyncio.get_event_loop()
    base._loop = loop

    db = await found.open()
    # clean database
    tr = db._create_transaction()
    tr.clear_range(b"", b"\xff")
    await tr.commit()

    return db


@pytest.mark.asyncio
async def test_yiwen_empty():
    db = await open()
    from socialiter.data.space.yiwen import Yiwen

    yiwen = Yiwen(b"test-yiwen")
    tuples = await yiwen.all(db)
    assert tuples == []


@pytest.mark.asyncio
async def test_yiwen_one_tuple():
    db = await open()
    from socialiter.data.space.yiwen import Yiwen

    yiwen = Yiwen(b"test-yiwen")
    yiwen.predicate(3, lambda x: True, None, True)
    expected = (2, 3, 4)
    await yiwen.add(db, expected)
    tuples = await yiwen.all(db)
    assert tuples == [expected]


@pytest.mark.asyncio
async def test_yiwen_many_tuples():
    db = await open()
    from socialiter.data.space.yiwen import Yiwen

    yiwen = Yiwen(b"test-yiwen")
    yiwen.predicate(2, lambda x: True, None, True)
    yiwen.predicate(9, lambda x: True, None, True)
    yiwen.predicate(3, lambda x: True, None, True)
    expected = [(1, 2, 3), (1, 9, 8), (1, 3, 3)]
    expected.sort()  # XXX: yiwen keeps ordering
    await yiwen.add(db, *expected)
    tuples = await yiwen.all(db)
    assert tuples == expected


@pytest.mark.asyncio
async def test_yiwen_where_one_pattern():
    db = await open()
    from socialiter.data.space.yiwen import Yiwen
    from socialiter.data.space.yiwen import var

    yiwen = Yiwen(b"test-yiwen")
    yiwen.predicate('title', lambda x: True, None, True)
    yiwen.predicate('description', lambda x: True, None, True)
    data = [
        ("uid1", "title", "yiwen"),
        ("uid1", "description", "rdf / sparql for humans"),
        ("uid2", "title", "hyperdev.fr"),
        ("uid2", "description", "forward and beyond!"),
    ]
    await yiwen.add(db, *data)
    out = await yiwen.where(db, ("uid1", var("key"), var("value")))
    out = [dict(x.items()) for x in out]
    assert out == [
        {"key": "description", "value": "rdf / sparql for humans"},
        {"key": "title", "value": "yiwen"},
    ]


@pytest.mark.asyncio
async def test_multiple_seeds():
    # prepare
    db = await open()
    from socialiter.data.space.yiwen import Yiwen
    from socialiter.data.space.yiwen import var

    yiwen = Yiwen(b"test-yiwen")

    yiwen.predicate('number', lambda x: True, None, True)
    yiwen.predicate('name', lambda x: True, None, True)

    tuples = [
        ("seed0", "name", "abki"),
        ("seed1", "name", "abki"),
        ("zero", "number", "seed0"),
        ("one", "number", "seed1"),
    ]
    await yiwen.add(db, *tuples)
    # exec
    patterns = (
        (var('seed'), "name", "abki"),
        (var('number'), "number", var("seed")),
    )
    out = await yiwen.where(db, *patterns)
    # check
    assert ["zero", "one"] == [o["number"] for o in out]


@pytest.mark.asyncio
async def test_yiwen_where_several_pattern():
    db = await open()
    from socialiter.data.space.yiwen import Yiwen
    from socialiter.data.space.yiwen import var

    yiwen = Yiwen(b"test-yiwen")
    yiwen.predicate('title', lambda x: True, None, True)
    yiwen.predicate('description', lambda x: True, None, True)
    yiwen.predicate('blog', lambda x: True, None, True)
    data = [
        ("uid1", "title", "yiwen"),
        ("uid1", "description", "rdf / sparql for humans"),
        ("uid3", "blog", "uid1"),
        ("uid3", "title", "yiwen query language"),
        ("uid2", "title", "hyperdev.fr"),
        ("uid2", "description", "forward and beyond!"),
    ]
    await yiwen.add(db, *data)
    patterns = [
        (var("blog"), "title", "yiwen"),
        (var("post"), "blog", var("blog")),
        (var("post"), "title", var("title")),
    ]
    out = await yiwen.where(db, *patterns)
    out = [dict(x.items()) for x in out]
    assert out == [{"blog": "uid1", "post": "uid3", "title": "yiwen query language"}]


@pytest.mark.asyncio
async def test_yiwen_stuff():
    db = await open()
    from socialiter.data.space.yiwen import Yiwen
    from socialiter.data.space.yiwen import var

    yiwen = Yiwen(b"test-yiwen")
    yiwen.predicate('is a', lambda x: True, None, True)
    yiwen.predicate('name', lambda x: True, None, True)
    yiwen.predicate('created-at', lambda x: True, None, True)
    yiwen.predicate('expression', lambda x: True, None, True)
    yiwen.predicate('modified-at', lambda x: True, None, True)
    yiwen.predicate('html', lambda x: True, None, True)
    yiwen.predicate('actor', lambda x: True, None, True)
    yiwen.predicate('followee', lambda x: True, None, True)
    yiwen.predicate('follower', lambda x: True, None, True)

    tuples = [
        # abki
        ("74c69c2adfef4648b286b720c69a334b", "is a", "user"),
        ("74c69c2adfef4648b286b720c69a334b", "name", "abki"),
        # amz31
        ("f1e18a79a9564018b2cccef24911e931", "is a", "user"),
        ("f1e18a79a9564018b2cccef24911e931", "name", "amz31"),
        # abki says poor man social network
        ("78ad80d0cb7e4975acb1f222c960901d", "created-at", 1536859544),
        ("78ad80d0cb7e4975acb1f222c960901d", "expression", "poor man social network"),
        (
            "78ad80d0cb7e4975acb1f222c960901d",
            "html",
            "<p>poor man social network</p>\n",
        ),
        ("78ad80d0cb7e4975acb1f222c960901d", "modified-at", 1536859544),
        (
            "78ad80d0cb7e4975acb1f222c960901d",
            "actor",
            "74c69c2adfef4648b286b720c69a334b",
        ),
        # amz31 follow abki
        (
            "d563fd7cdbd84c449d36f1e6cf5893a3",
            "followee",
            "74c69c2adfef4648b286b720c69a334b",
        ),  # noqa
        (
            "d563fd7cdbd84c449d36f1e6cf5893a3",
            "follower",
            "f1e18a79a9564018b2cccef24911e931",
        ),  # noqa
        # abki says socialite for the win
        ("fe066559ce894d9caf2bca63c42d98a8", "created-at", 1536859522),
        ("fe066559ce894d9caf2bca63c42d98a8", "expression", "socialite for the win!"),
        ("fe066559ce894d9caf2bca63c42d98a8", "html", "<p>socialite for the win!</p>\n"),
        ("fe066559ce894d9caf2bca63c42d98a8", "modified-at", 1536859522),
        (
            "fe066559ce894d9caf2bca63c42d98a8",
            "actor",
            "74c69c2adfef4648b286b720c69a334b",
        ),
    ]
    await yiwen.add(db, *tuples)
    everything = await yiwen.all(db)
    assert len(everything) == len(tuples)

    user = "f1e18a79a9564018b2cccef24911e931"
    patterns = (
        (var("follow"), "follower", user),
        (var("follow"), "followee", var("followee")),
        (var("expression"), "actor", var("followee")),
        (var("expression"), "html", var("html")),
        (var("expression"), "modified-at", var("modified-at")),
        (var("followee"), "name", var("name")),
    )
    out = await yiwen.where(db, *patterns)
    out.sort(key=lambda x: x["modified-at"], reverse=True)
    assert len(out) == 2
    assert [b["expression"] for b in out] == [
        "78ad80d0cb7e4975acb1f222c960901d",
        "fe066559ce894d9caf2bca63c42d98a8",
    ]  # noqa
