import pytest
import cyberpandas
import pandas as pd
import pandas.util.testing as tm

dd = pytest.importorskip('dask.dataframe')
dask = pytest.importorskip("dask")
da = pytest.importorskip("dask.array")


def test_constructor():
    a = cyberpandas.to_ipaddress([1, 2, 3, 4]).data
    b = da.from_array(a, chunks=2)

    iparr = cyberpandas.IPArray(b)
    assert isinstance(iparr.data, da.Array)
    da.utils.assert_eq(iparr.data, b)
    da.utils.assert_eq(iparr.data, a)

    result, = dask.compute(iparr)
    assert isinstance(result, cyberpandas.IPArray)


def test_basics():
    a = cyberpandas.to_ipaddress([1, 2, 3, 4]).data
    b = da.from_array(a, chunks=2)

    c = cyberpandas.IPArray(a)
    d = cyberpandas.IPArray(b)

    da.utils.assert_eq(c.isna(), d.isna())
    da.utils.assert_eq(c.is_ipv4, d.is_ipv4)

    meta = dd.utils.meta_nonempty(pd.Series(c))
    expected = pd.Series(cyberpandas.IPArray(['0.0.0.1', '0.0.0.2']))
    tm.assert_series_equal(meta, expected)


def test_dask_series():
    a = cyberpandas.IPArray(cyberpandas.to_ipaddress([1, 2, 3, 4]).data)
    b = cyberpandas.IPArray(da.from_array(a.data, chunks=2)).to_dask_series()

    b.loc[0]


def test_accessor():
    a = cyberpandas.to_ipaddress([1, 2, 3, 4]).data
    a = pd.Series(cyberpandas.IPArray(a))
    b = dd.from_pandas(a, 2)

    dd.utils.assert_eq(a.ip.is_ipv4, b.ip.is_ipv4)
    dd.utils.assert_eq(a.ip.netmask(), b.ip.netmask())
