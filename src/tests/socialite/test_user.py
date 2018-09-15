import pytest

import trafaret as t

from socialite import user


def test_account_new_validate_empty():
    data = dict()
    with pytest.raises(t.DataError):
        assert user.user_validate(data)


def _test_account_new_validate_valid():
    data = dict(  # nosec
        username="amirouche",
        password="FooBar!42count",
        validation="FooBar!42count",
    )
    assert user.user_validate(data)


def test_account_new_validate_invalid_password():
    data = dict(  # nosec
        username="peon",
        password="toosimple",
        validation="toosimple",
    )
    with pytest.raises(t.DataError) as exc:
        assert user.user_validate(data)
        assert exc.as_dict()['password']
