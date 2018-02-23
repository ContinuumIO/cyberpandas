import ipaddress

import pytest

from cyberpandas import parser, IPArray


@pytest.mark.parametrize('values', [
    [u'192.168.1.1',
     u'2001:0db8:85a3:0000:0000:8a2e:0370:7334'],
    [3232235777,
     42540766452641154071740215577757643572],
    [b'\xc0\xa8\x01\x01',
     b' \x01\r\xb8\x85\xa3\x00\x00\x00\x00\x8a.\x03ps4'],
])
def test_to_ipaddress(values):
    result = parser.to_ipaddress(values)
    expected = IPArray.from_pyints([
        3232235777,
        42540766452641154071740215577757643572
    ])
    assert result.equals(expected)


def test_to_ipaddress_edge():
    ip_int = 2 ** 64
    result = parser.to_ipaddress([ip_int]).to_pyipaddress()[0]
    assert int(result) == ip_int


def test_to_ipaddress_scalar():
    result = parser.to_ipaddress(1)
    expected = parser.to_ipaddress([1])
    assert len(result) == 1
    assert all(result == expected)


@pytest.mark.parametrize('val, expected', [
    (u'192.168.1.1', ipaddress.IPv4Address(u'192.168.1.1')),
    (100, ipaddress.IPv4Address(100)),
    (ipaddress.IPv4Address(100), ipaddress.IPv4Address(100)),
    (2**64, ipaddress.IPv6Address(2**64)),
    (u'192.168.0.0/28', ipaddress.IPv4Network(u'192.168.0.0/28')),
    (ipaddress.IPv4Network(u'192.168.0.0/28'),
     ipaddress.IPv4Network(u'192.168.0.0/28')),
    (u'2001:db00::0/24', ipaddress.IPv6Network(u'2001:db00::0/24')),
])
def test_as_ip_object(val, expected):
    result = parser._as_ip_object(val)
    assert result == expected


@pytest.mark.parametrize("val", [
    u"129", -1
])
def test_as_ip_object_raises(val):
    with pytest.raises(ValueError):
        parser._as_ip_object(val)
