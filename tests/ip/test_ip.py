import ipaddress
import operator

import pytest
import six
from hypothesis.strategies import integers, lists, tuples
from hypothesis import given, example

import numpy as np
import numpy.testing as npt
import pandas as pd
import cyberpandas as ip
import pandas.util.testing as tm
from cyberpandas.common import _U8_MAX


def test_make_container():
    values = ip.IPArray.from_pyints([1, 2, 3])
    npt.assert_array_equal(
        values.data,
        np.array([(0, 1),
                  (0, 2),
                  (0, 3)], dtype=values.dtype._record_type)
    )


def test_repr_works():
    values = ip.IPArray.from_pyints([0, 1, 2, 3, 2**32, 2**64 + 1])
    result = repr(values)
    if six.PY2:
        expected = ("IPArray([u'0.0.0.0', u'0.0.0.1', u'0.0.0.2', u'0.0.0.3', "
                    "u'::1:0:0', u'::1:0:0:0:1'])")
    else:
        expected = ("IPArray(['0.0.0.0', '0.0.0.1', '0.0.0.2', '0.0.0.3', "
                    "'::1:0:0', '::1:0:0:0:1'])")
    assert result == expected


def test_isna():
    v = ip.IPArray.from_pyints([0, 2, 2 ** 64, 2 ** 64 + 1, 2 ** 64 + 2])
    r1 = v.isna()
    r2 = pd.isna(v)
    expected = np.array([True, False, False, False, False])

    np.testing.assert_array_equal(r1, expected)
    np.testing.assert_array_equal(r2, expected)


def test_array():
    v = ip.IPArray.from_pyints([1, 2, 3])
    result = np.array(v)
    expected = np.array([
        ipaddress.IPv4Address(1),
        ipaddress.IPv4Address(2),
        ipaddress.IPv4Address(3),
    ])
    tm.assert_numpy_array_equal(result, expected)


def test_tolist():
    v = ip.IPArray.from_pyints([1, 2, 3])
    result = v.tolist()
    expected = [(0, 1), (0, 2), (0, 3)]
    assert result == expected


def test_to_pyipaddress():
    v = ip.IPArray.from_pyints([1, 2, 3])
    result = v.to_pyipaddress()
    expected = [
        ipaddress.ip_address(1),
        ipaddress.ip_address(2),
        ipaddress.ip_address(3),
    ]
    assert result == expected


def test_isip():
    v = ip.to_ipaddress([
        u'192.168.1.1',
        u'2001:0db8:85a3:0000:0000:8a2e:0370:7334',
    ])
    result = v.is_ipv4
    expected = np.array([True, False])
    tm.assert_numpy_array_equal(result, expected)

    result = v.is_ipv6
    expected = np.array([False, True])
    tm.assert_numpy_array_equal(result, expected)


def test_equality():
    v1 = ip.to_ipaddress([
        u'192.168.1.1',
        u'2001:0db8:85a3:0000:0000:8a2e:0370:7334',
    ])
    assert np.all(v1 == v1)
    assert v1.equals(v1)

    v2 = ip.to_ipaddress([
        u'192.168.1.2',
        u'2001:0db8:85a3:0000:0000:8a2e:0370:7334',
    ])
    result = v1 == v2
    expected = np.array([False, True])
    tm.assert_numpy_array_equal(result, expected)

    result = bool(v1.equals(v2))
    assert result is False

    with pytest.raises(TypeError):
        v1.equals("a")


@pytest.mark.parametrize('other', [
    1, '192.168.1.1', b'1'
])
def test_ops_other(other):
    arr = ip.IPArray([1, 2, 3])

    with pytest.raises(TypeError):
        arr == other


@pytest.mark.parametrize('other', [
    ipaddress.IPv4Address(1),
    ipaddress.IPv6Address(1),
])
def test_equality_ipaddress(other):
    arr = ip.IPArray([0, 1, 2**64 + 1])
    result = arr == other
    expected = np.array([False, True, False])
    tm.assert_numpy_array_equal(result, expected)


@pytest.mark.parametrize('op', [
    operator.lt,
    operator.le,
    operator.ge,
    operator.gt,
])
@pytest.mark.skipif(six.PY2, reason="Flexible comparisons")
def test_comparison_raises(op):
    arr = ip.IPArray([0, 1, 2])
    with pytest.raises(TypeError):
        op(arr, 'a')

    with pytest.raises(TypeError):
        op('a', arr)


@given(
    tuples(
        lists(integers(min_value=0, max_value=2**128 - 1)),
        lists(integers(min_value=0, max_value=2**128 - 1))
    ).filter(lambda x: len(x[0]) == len(x[1]))
)
@example((1, 1))
@example((0, 0))
@example((0, 1))
@example((1, 0))
@example((1, 2))
@example((2, 1))
def test_ops(tup):
    a, b = tup
    v1 = ip.IPArray(a)
    v2 = ip.IPArray(b)

    r1 = v1 <= v2
    r2 = v2 >= v1
    tm.assert_numpy_array_equal(r1, r2)


@pytest.mark.xfail(reason='upstream')
def test_value_counts():
    x = ip.IPArray([0, 0, 1])
    result = x.value_counts()
    assert len(result)


def test_iter_works():
    x = ip.IPArray([0, 1, 2])
    result = list(x)
    expected = [
        ipaddress.IPv4Address(0),
        ipaddress.IPv4Address(1),
        ipaddress.IPv4Address(2),
    ]
    assert result == expected


def test_topyints():
    values = [0, 1, 2**32]
    arr = ip.IPArray(values)
    result = arr.to_pyints()
    assert result == values


@pytest.mark.parametrize('prop', [
    'version',
    'is_multicast',
    'is_private',
    'is_global',
    'is_unspecified',
    'is_reserved',
    'is_loopback',
    'is_link_local',
])
def test_attributes(prop):
    addrs = [ipaddress.ip_address(0),
             ipaddress.ip_address(1)]
    arr = ip.IPArray(addrs)
    result = getattr(arr, prop)
    expected = np.array([getattr(addr, prop)
                         for addr in addrs])
    tm.assert_numpy_array_equal(result, expected)


def test_isin_all4():
    s = ip.IPArray([u'192.168.1.1', u'255.255.255.255'])
    result = s.isin([u'192.168.1.0/24'])
    expected = np.array([True, False])
    tm.assert_numpy_array_equal(result, expected)


def test_isin_all6():
    s = ip.IPArray([u'2001:db8::1', u'2001:db9::1'])
    result = s.isin([u'2001:db8::0/96'])
    expected = np.array([True, False])
    tm.assert_numpy_array_equal(result, expected)


def test_isin_mix():
    s = ip.IPArray([u'192.168.1.1', u'255.255.255.255',
                    u'2001:db8::1', u'2001:db9::1'])

    result = s.isin([u'192.168.1.0/24'])
    expected = np.array([True, False, False, False])
    tm.assert_numpy_array_equal(result, expected)

    result = s.isin([u'2001:db8::0/96'])
    expected = np.array([False, False, True, False])
    tm.assert_numpy_array_equal(result, expected)

    result = s.isin([u'192.168.1.0/24', u'2001:db8::0/96'])
    expected = np.array([True, False, True, False])
    tm.assert_numpy_array_equal(result, expected)

    s = ip.IPArray([u'192.168.1.1', u'192.168.1.2',
                    u'255.255.255.255'])
    result = s.isin([u'192.168.1.0/24'])
    expected = np.array([True, True, False])
    tm.assert_numpy_array_equal(result, expected)


def test_isin_iparray():
    s = ip.IPArray([10, 20, 20, 30])
    result = s.isin(ip.IPArray([30, 20]))
    expected = np.array([False, True, True, True])
    tm.assert_numpy_array_equal(result, expected)


def test_getitem_scalar():
    ser = ip.IPArray([0, 1, 2])
    result = ser[1]
    assert result == ipaddress.ip_address(1)


def test_getitem_slice():
    ser = ip.IPArray([0, 1, 2])
    result = ser[1:]
    expected = ip.IPArray([1, 2])
    assert result.equals(expected)


@pytest.mark.parametrize('value', [
    u'0.0.0.10',
    10,
    ipaddress.ip_address(10),
])
def test_setitem_scalar(value):
    ser = ip.IPArray([0, 1, 2])
    ser[1] = ipaddress.ip_address(value)
    expected = ip.IPArray([0, 10, 2])
    assert ser.equals(expected)


def test_setitem_array():
    ser = ip.IPArray([0, 1, 2])
    ser[[1, 2]] = [10, 20]
    expected = ip.IPArray([0, 10, 20])
    assert ser.equals(expected)


def test_bytes_roundtrip():
    arr = ip.IPArray([1, 2, 3, _U8_MAX + 10])
    bytestring = arr.to_bytes()
    assert isinstance(bytestring, bytes)

    result = ip.IPArray.from_bytes(bytestring)
    assert result.equals(arr)


def test_unique():
    arr = ip.IPArray([3, 3, 1, 2, 3, _U8_MAX + 1])
    result = arr.unique()
    assert isinstance(result, ip.IPArray)

    result = result.astype(object)
    expected = pd.unique(arr.astype(object))
    tm.assert_numpy_array_equal(result, expected)


def test_factorize():
    arr = ip.IPArray([3, 3, 1, 2, 3, _U8_MAX + 1])
    labels, uniques = arr.factorize()
    expected_labels, expected_uniques = pd.factorize(arr.astype(object))

    assert isinstance(uniques, ip.IPArray)

    uniques = uniques.astype(object)
    tm.assert_numpy_array_equal(labels, expected_labels)
    tm.assert_numpy_array_equal(uniques, expected_uniques)
