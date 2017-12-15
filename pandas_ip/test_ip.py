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
