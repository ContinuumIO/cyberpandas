"""Tests involving pandas, not just the new array.
"""
import pytest
from hypothesis.strategies import integers, lists
from hypothesis import given
import pandas as pd
import pandas.util.testing as tm

import pandas_ip as ip


# ----------------------------------------------------------------------------
# Block Constructors
# ----------------------------------------------------------------------------

def test_make_block():
    values = ip.IPAddress.from_pyints([1, 2, 3])
    block = ip.IPBlock(values, slice(0, 3))
    assert isinstance(block, ip.IPBlock)
    assert isinstance(block.dtype, ip.IPType)
    assert block.ndim == 1


def test_series_from_block():
    values = ip.IPAddress.from_pyints([1, 2, 3])
    block = ip.IPBlock(values, slice(0, 3))

    result = pd.Series(block, index=pd.RangeIndex(3), fastpath=True)
    assert isinstance(result.dtype, ip.IPType)


def test_to_series_from_block():
    values = ip.IPAddress.from_pyints([1, 2, 3])
    block = ip.IPBlock(values, slice(0, 3))
    expected = pd.Series(block, index=pd.RangeIndex(3), fastpath=True)
    result = values.to_series()
    assert isinstance(result._data.blocks[0], ip.IPBlock)
    tm.assert_series_equal(result, expected)
    assert isinstance(result.dtype, ip.IPType)
    assert result.name is None

    result = values.to_series(name='foo')
    assert result.name == 'foo'


def test_dataframe_from_blocks():
    values = ip.IPAddress.from_pyints([1, 2, 3])
    blocks = (ip.IPBlock(values, slice(0, 1)),)
    axes = [pd.Index(['a']), pd.RangeIndex(3)]
    bm = pd.core.internals.BlockManager(blocks, axes)
    result = pd.DataFrame(bm)

    assert isinstance(result.dtypes['a'], ip.IPType)


# ----------------------------------------------------------------------------
# Block Methods
# ----------------------------------------------------------------------------


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


# ----------------------------------------------------------------------------
# Public Constructors
# ----------------------------------------------------------------------------


def test_series_constructor():
    v = ip.IPAddress.from_pyints([1, 2, 3])
    result = pd.Series(v)
    expected = v.to_series()
    tm.assert_series_equal(result, expected)
    assert isinstance(result._data.blocks[0], ip.IPBlock)


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
    s = pd.Series([1, 2, 3], index=ip.IPAddressIndex([0, 1, 2]))
    repr(s)


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
