import pytest

from cyberpandas import dtypes


@pytest.mark.parametrize('value', [
    "192.168.0.1",
    3232235521,
])
@pytest.mark.xfail
def test_is_ipv4(value):
    assert dtypes.is_ipv4(value)


@pytest.mark.parametrize('value', [
    '123.123.1',
    2 ** 32,
])
def test_is_not_ipv4(value):
    assert not dtypes.is_ipv4(value)
