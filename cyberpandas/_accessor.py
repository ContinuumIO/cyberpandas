import pandas as pd

from ._compat import HAS_DASK


def delegated_method(method, index, name, *args, **kwargs):
    values = method(*args, **kwargs)
    if HAS_DASK and hasattr(index, '__dask_graph__'):
        import dask.dataframe as dd
        # TODO; pass this info ahead of time, from the accessor

        result = dd.from_dask_array(values, index=index)
        result.name = name
        return result

    return pd.Series(method(*args, **kwargs), index, name=name)


class Delegated:
    # Descriptor for delegating attribute access to from
    # a Series to an underlying array

    def __init__(self, name):
        self.name = name

    def __get__(self, obj, type=None):
        index = object.__getattribute__(obj, '_index')
        name = object.__getattribute__(obj, '_name')
        result = self._get_result(obj)

        if HAS_DASK and hasattr(result, '__dask_graph__'):
            import dask.dataframe as dd

            result = dd.from_dask_array(result, index=index)
            result.name = name
            return result

        return pd.Series(result, index, name=name)

    def _getresult(self, obj, type=None):
        raise NotImplementedError


class DelegatedProperty(Delegated):
    def _get_result(self, obj, type=None):
        return getattr(object.__getattribute__(obj, '_data'), self.name)


class DelegatedMethod(Delegated):
    def __get__(self, obj, type=None):
        index = object.__getattribute__(obj, '_index')
        name = object.__getattribute__(obj, '_name')
        method = getattr(object.__getattribute__(obj, '_data'), self.name)
        return delegated_method(method, index, name)
