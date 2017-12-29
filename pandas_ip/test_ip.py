import ipaddress

import numpy as np
import numpy.testing as npt
import pandas as pd
import pandas_ip as ip
import pandas.util.testing as tm


def test_make_container():
    values = ip.IPAddress.from_pyints([1, 2, 3])
    npt.assert_array_equal(
        values.data,
        np.array([(0, 1),
                  (0, 2),
                  (0, 3)], dtype=values.dtype.base)
    )


def test_repr_works():
    values = ip.IPAddress.from_pyints([1, 2, 3])
    block = ip.IPBlock(values, slice(0, 3))
    block.formatting_values()


def test_isna():
    v = ip.IPAddress.from_pyints([0, 2, 3])
    r1 = v.isna()
    r2 = pd.isna(v)
    expected = np.array([True, False, False])

    np.testing.assert_array_equal(r1, expected)
    np.testing.assert_array_equal(r2, expected)


def test_array():
    v = ip.IPAddress.from_pyints([1, 2, 3])
    result = np.array(v)
    expected = np.array([(0, 1), (0, 2), (0, 3)],
                        dtype=ip.IPType.base)
    tm.assert_numpy_array_equal(result, expected)


def test_tolist():
    v = ip.IPAddress.from_pyints([1, 2, 3])
    result = v.tolist()
    expected = [(0, 1), (0, 2), (0, 3)]
    assert result == expected


def test_to_pyipaddress():
    v = ip.IPAddress.from_pyints([1, 2, 3])
    result = v.to_pyipaddress()
    expected = [
        ipaddress.ip_address(1),
        ipaddress.ip_address(2),
        ipaddress.ip_address(3),
    ]
    assert result == expected


def test_repr():
    v = ip.to_ipaddress([
        '192.168.1.1',
        '2001:0db8:85a3:0000:0000:8a2e:0370:7334',
    ])
    e = "<IPAddress(['192.168.1.1', '0:8a2e:370:7334:2001:db8:85a3:0'])>"
    assert repr(v) == e


def test_isip():
    v = ip.to_ipaddress([
        '192.168.1.1',
        '2001:0db8:85a3:0000:0000:8a2e:0370:7334',
    ])
    result = v.is_ipv4
    expected = np.array([True, False])
    tm.assert_numpy_array_equal(result, expected)

    result = v.is_ipv6
    expected = np.array([False, True])
    tm.assert_numpy_array_equal(result, expected)


def test_equality():
    v1 = ip.to_ipaddress([
        '192.168.1.1',
        '2001:0db8:85a3:0000:0000:8a2e:0370:7334',
    ])
    assert np.all(v1 == v1)
    assert v1.equals(v1)

    v2 = ip.to_ipaddress([
        '192.168.1.2',
        '2001:0db8:85a3:0000:0000:8a2e:0370:7334',
    ])
    result = v1 == v2
    expected = np.array([False, True])
    tm.assert_numpy_array_equal(result, expected)

    result = bool(v1.equals(v2))
    assert result is False


def test_value_counts():
    x = ip.IPAddress([0, 0, 1])
    result = x.value_counts()
    assert len(result)
