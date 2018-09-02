import pytest

import trafaret as t

from socialite.user import account_new_validate
import found.v510 as fdb


def test_pack_unpack():
    value = ((1, ('abc',)), ('d', 'e', 'f'))
    assert fdb.unpack(fdb.pack(value)) == value


@pytest.mark.asyncio
async def test_range():
    db = await fdb.open()
    tx = db._create_transaction()
    for number in range(10):
        tx.set(fdb.pack((number,)), fdb.pack((str(number),)))
    await tx.commit()

    tx = db._create_transaction()
    out = list()
    async for item in tx.get_range(fdb.pack((1,)), fdb.pack((8,))):
        out.append(item)
    await tx.commit()

    for (key, value), index in zip(out, range(10)[1:-1]):
        assert fdb.unpack(key)[0] == index
        assert fdb.unpack(value)[0] == str(index)


def test_account_new_validate_empty():
    data = dict()
    with pytest.raises(t.DataError):
        assert account_new_validate(data)


def _test_account_new_validate_valid():
    data = dict(
        username="amirouche",
        password="FooBar!42count",
        validation="FooBar!42count",
        bio="energy hacker",
    )
    assert account_new_validate(data)


def test_account_new_validate_invalid_password():
    data = dict(
        username="peon",
        password="toosimple",
        validation="toosimple",
        bio="much wow",
    )
    with pytest.raises(t.DataError) as exc:
        assert account_new_validate(data)
        assert exc.as_dict()['password']
