import pytest

from pandas_ip import parser


@pytest.mark.parametrize('value', [
    "192.168.0.1",
    3232235521,
])
def test_is_ipv4(value):
    assert parser.is_ipv4(value)


@pytest.mark.parametrize('value', [
    '123.123.1',
    2 ** 32,
])
def test_is_not_ipv4(value):
    assert not parser.is_ipv4(value)


@pytest.mark.parametrize('s', [
    "2001:0db8:85a3:0000:0000:8a2e:0370:7334"
])
def test_parse_str(s):
    parser._parse_ipv4_str(s)
