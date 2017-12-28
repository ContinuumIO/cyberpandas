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


def test_make_block():
    values = ip.IPAddress.from_pyints([1, 2, 3])
    block = ip.IPBlock(values, slice(0, 3))
    assert isinstance(block, ip.IPBlock)
    assert block.dtype is ip.IPType
    assert block.ndim == 1


def test_repr_works():
    values = ip.IPAddress.from_pyints([1, 2, 3])
    block = ip.IPBlock(values, slice(0, 3))
    block.formatting_values()


def test_series_from_block():
    values = ip.IPAddress.from_pyints([1, 2, 3])
    block = ip.IPBlock(values, slice(0, 3))

    result = pd.Series(block, index=pd.RangeIndex(3), fastpath=True)
    assert result.dtype is ip.IPType


def test_to_series_from_block():
    values = ip.IPAddress.from_pyints([1, 2, 3])
    block = ip.IPBlock(values, slice(0, 3))
    expected = pd.Series(block, index=pd.RangeIndex(3), fastpath=True)
    result = values.to_series()
    tm.assert_series_equal(result, expected)
    assert result.dtype is ip.IPType
    assert result.name is None

    result = values.to_series(name='foo')
    assert result.name == 'foo'


def test_dataframe_from_blocks():
    values = ip.IPAddress.from_pyints([1, 2, 3])
    blocks = (ip.IPBlock(values, slice(0, 1)),)
    axes = [pd.Index(['a']), pd.RangeIndex(3)]
    bm = pd.core.internals.BlockManager(blocks, axes)
    result = pd.DataFrame(bm)

    assert result.dtypes['a'] is ip.IPType


def test_concatenate_blocks():
    v1 = ip.IPAddress.from_pyints([1, 2, 3])
    b1 = ip.IPBlock(v1, slice(0, 3))

    s = pd.Series(b1, index=pd.RangeIndex(3), fastpath=True)
    result = pd.concat([s, s], ignore_index=True)
    expected = pd.Series(
        ip.IPBlock(ip.IPAddress.from_pyints([1, 2, 3, 1, 2, 3]),
                   placement=slice(0, 6)),
        index=pd.RangeIndex(6),
        fastpath=True)
    tm.assert_series_equal(result, expected)


def test_series_constructor():
    v = ip.IPAddress.from_pyints([1, 2, 3])
    result = pd.Series(v)
    expected = v.to_series()
    tm.assert_series_equal(result, expected)
    assert isinstance(result._data.blocks[0], ip.IPBlock)


def test_dataframe_constructor():
    v = ip.IPAddress.from_pyints([1, 2, 3])
    df = pd.DataFrame({"A": v})
    tm.assert_series_equal(df.dtypes, pd.Series([ip.IPType], ['A']))
    assert df.shape == (3, 1)
    str(df)


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
