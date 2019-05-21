from functools import singledispatch
from collections import abc
import numpy as np

try:
    import dask.array
    import dask.dataframe
except ImportError:
    HAS_DASK = False
else:
    HAS_DASK = True


@singledispatch
def asarray(values, *args, **kwargs):
    return np.asarray(values, *args, **kwargs)


@singledispatch
def atleast_1d(values):
    return np.atleast_1d(values)


def is_dask_collection(x):
    if HAS_DASK:
        import dask
        return dask.is_dask_collection(x)
    return False


if HAS_DASK:
    @asarray.register(dask.array.Array)
    def _(values, *args, **kwargs):
        return dask.array.asarray(values, *args, **kwargs)

    @atleast_1d.register(dask.array.Array)
    def _(values):
        return dask.array.atleast_1d(values)


def is_array_like(obj):
    attrs = set(dir(obj))
    return bool(attrs & {'__array__', 'ndim', 'dtype'})


def is_list_like(obj):
    return isinstance(obj, abc.Sized)
