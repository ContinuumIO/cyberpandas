"""Tests involving pandas, not just the new array.
"""
import ipaddress

import pytest
from hypothesis.strategies import integers, lists
from hypothesis import given
import pandas as pd
from pandas.core.internals import ExtensionBlock
import pandas.util.testing as tm

import pandas_ip as ip


# ----------------------------------------------------------------------------
# Block Methods
# ----------------------------------------------------------------------------


def test_concatenate_blocks():
    v1 = ip.IPAddress.from_pyints([1, 2, 3])
    s = pd.Series(v1, index=pd.RangeIndex(3), fastpath=True)
    result = pd.concat([s, s], ignore_index=True)
    expected = pd.Series(ip.IPAddress.from_pyints([1, 2, 3, 1, 2, 3]))
    tm.assert_series_equal(result, expected)


# ----------------------------------------------------------------------------
# Public Constructors
# ----------------------------------------------------------------------------


def test_series_constructor():
    v = ip.IPAddress.from_pyints([1, 2, 3])
    result = pd.Series(v)
    assert result.dtype == v.dtype
    assert isinstance(result._data.blocks[0], ExtensionBlock)


def test_dataframe_constructor():
    v = ip.IPAddress.from_pyints([1, 2, 3])
    df = pd.DataFrame({"A": v})
    assert isinstance(df.dtypes['A'], ip.IPType)
    assert df.shape == (3, 1)
    str(df)


def test_dataframe_from_series_no_dict():
    s = pd.Series(ip.IPAddress([1, 2, 3]))
    result = pd.DataFrame(s)
    expected = pd.DataFrame({0: s})
    tm.assert_frame_equal(result, expected)

    s = pd.Series(ip.IPAddress([1, 2, 3]), name='A')
    result = pd.DataFrame(s)
    expected = pd.DataFrame({'A': s})
    tm.assert_frame_equal(result, expected)


def test_dataframe_from_series():
    s = pd.Series(ip.IPAddress([0, 1, 2]))
    c = pd.Series(pd.Categorical(['a', 'b']))
    result = pd.DataFrame({"A": s, 'B': c})
    assert isinstance(result.dtypes['A'], ip.IPType)


def test_index_constructor():
    result = ip.IPAddressIndex([0, 1, 2])
    assert isinstance(result, ip.IPAddressIndex)
    assert result._data.equals(ip.IPAddress([0, 1, 2]))
    assert repr(result) == "IPAddressIndex(['0.0.0.0', '0.0.0.1', '0.0.0.2'])"


def test_series_with_index():
    ser = pd.Series([1, 2, 3], index=ip.IPAddressIndex([0, 1, 2]))
    repr(ser)


def test_getitem_scalar():
    ser = pd.Series(ip.IPAddress([0, 1, 2]))
    result = ser[1]
    assert result == ipaddress.ip_address(1)


def test_getitem_slice():
    ser = pd.Series(ip.IPAddress([0, 1, 2]))
    result = ser[1:]
    expected = pd.Series(ip.IPAddress([1, 2]), index=range(1, 3))
    tm.assert_series_equal(result, expected)


def test_setitem_scalar():
    ser = pd.Series(ip.IPAddress([0, 1, 2]))
    ser[1] = ipaddress.ip_address(10)
    expected = pd.Series(ip.IPAddress([0, 10, 2]))
    tm.assert_series_equal(ser, expected)


# --------------
# Public Methods
# --------------


@pytest.mark.xfail(reason="upstream")
def test_value_counts():
    result = pd.Series(ip.IPAddress([1, 1, 2, 3, 3, 3])).value_counts()
    expected = pd.Series([3, 2, 1],
                         index=ip.IPAddressIndex([3, 1, 2]))
    tm.assert_series_equal(result, expected)


@given(lists(integers(min_value=1, max_value=2**128 - 1)))
def test_argsort(ints):
    pass
    # result = pd.Series(ip.IPAddress(ints)).argsort()
    # expected = pd.Series(ints).argsort()
    # tm.assert_series_equal(result.ip.to_pyints(), expected)
