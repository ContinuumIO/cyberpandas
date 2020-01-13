import pandas as pd

from ._compat import is_dask_collection


def delegated_method(method, index, name, *args, **kwargs):
    values = method(*args, **kwargs)
    return wrap_result(values, index, name)


def wrap_result(values, index, name):
    from cyberpandas.ip_array import IPType

    if is_dask_collection(values):
        import dask.array as da
        import dask.dataframe as dd

        if isinstance(values.dtype, IPType):
            return values.to_dask_series(index=index, name=name)

        elif isinstance(values, da.Array):
            return dd.from_dask_array(values, columns=name, index=index)

    return pd.Series(values, index=index, name=name)


class Delegated:
    # Descriptor for delegating attribute access to from
    # a Series to an underlying array

    def __init__(self, name):
        self.name = name

    def __get__(self, obj, type=None):
        index = object.__getattribute__(obj, '_index')
        name = object.__getattribute__(obj, '_name')
        result = self._get_result(obj)
        return wrap_result(result, index, name)

    def _get_result(self, obj, type=None):
        raise NotImplementedError


class DelegatedProperty(Delegated):
    def _get_result(self, obj, type=None):
        return getattr(object.__getattribute__(obj, '_data'), self.name)


class DelegatedMethod(Delegated):
    def _get_result(self, obj, type=None):
        method = getattr(object.__getattribute__(obj, '_data'), self.name)
        values = method()
        return values
