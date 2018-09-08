import pytest
from socialite import fdb


def test_pack_unpack():
    value = ((1, ('abc',)), ('d', 'e', 'f'))
    assert fdb.unpack(fdb.pack(value)) == value


@pytest.mark.asyncio
async def test_range():
    db = await fdb.open()
    tr = db._create_transaction()
    for number in range(10):
        tr.set(fdb.pack((number,)), fdb.pack((str(number),)))
    await tr.commit()

    tr = db._create_transaction()
    out = list()
    async for item in tr.get_range(fdb.pack((1,)), fdb.pack((8,))):
        out.append(item)
    await tr.commit()

    for (key, value), index in zip(out, range(10)[1:-1]):
        assert fdb.unpack(key)[0] == index
        assert fdb.unpack(value)[0] == str(index)
