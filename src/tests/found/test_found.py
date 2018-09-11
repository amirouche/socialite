import asyncio
import pytest
from found.v510 import base
from socialite import fdb


def test_pack_unpack():
    value = ((1, ('abc',)), ('d', 'e', 'f'))
    assert fdb.unpack(fdb.pack(value)) == value


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
async def test_get():
    # preapre
    db = await open()
    tr = db._create_transaction()
    tr.clear_range(b'\b00', b'\xff')

    #
    out = await tr.get(b'test')
    assert out is None
    tr.set(b'test', b'test')
    out = await tr.get(b'test')
    assert out == b'test'



@pytest.mark.asyncio
async def test_range():
    # prepare
    db = await open()
    tr = db._create_transaction()
    tr.clear_range(b'', b'\xff')

    # exec
    for number in range(10):
        tr.set(fdb.pack((number,)), fdb.pack((str(number),)))
    await tr.commit()

    tr = db._create_transaction()
    out = list()
    async for item in tr.get_range(fdb.pack((1,)), fdb.pack((8,))):
        out.append(item)
    await tr.commit()

    # check
    for (key, value), index in zip(out, range(10)[1:-1]):
        assert fdb.unpack(key)[0] == index
        assert fdb.unpack(value)[0] == str(index)
