import numpy as np
import numpy.testing as npt
import pandas as pd
import pandas_ip as ip


def test_make_container():
    values = ip.IP([1, 2, 3])
    npt.assert_array_equal(
        values.ips,
        np.array([1, 2, 3])
    )

    npt.assert_array_equal(
        values._meta,
        np.array([1, 1, 1], dtype=np.uint8)
    )


def test_make_block():
    values = ip.IP([1, 2, 3])
    block = ip.IPBlock(values, slice(0, 3))
    assert isinstance(block, ip.IPBlock)
    assert block.dtype is ip.IPType
    assert block.ndim == 1


def test_repr_works():
    values = ip.IP([1, 2, 3])
    block = ip.IPBlock(values, slice(0, 3))
    block.formatting_values()


def test_series_from_block():
    values = ip.IP([1, 2, 3])
    block = ip.IPBlock(values, slice(0, 3))

    result = pd.Series(block, index=pd.RangeIndex(3), fastpath=True)
    assert result.dtype is ip.IPType


def test_dataframe_from_blocks():
    values = ip.IP([1, 2, 3])
    blocks = (ip.IPBlock(values, slice(0, 1)),)
    axes = [pd.Index(['a']), pd.RangeIndex(3)]
    bm = pd.core.internals.BlockManager(blocks, axes)
    result = pd.DataFrame(bm)

    assert result.dtypes['a'] is ip.IPType
