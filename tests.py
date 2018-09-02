import pytest

import trafaret as t

from socialite.socialite import account_new_validate


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
