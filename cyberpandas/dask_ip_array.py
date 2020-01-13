import ipaddress

import numpy as np
import dask.array as da
import dask.dataframe as dd
from dask.dataframe.extensions import (
    make_scalar, make_array_nonempty, register_series_accessor)
from .ip_array import IPAccessor, IPType, IPArray


@make_array_nonempty.register(IPType)
def _(dtype):
    return IPArray._from_sequence([1, 2], dtype=dtype)


@make_scalar.register(ipaddress.IPv4Address)
@make_scalar.register(ipaddress.IPv6Address)
def _(x):
    return ipaddress.ip_address(x)


@register_series_accessor("ip")
class DaskIPAccessor(IPAccessor):
    @staticmethod
    def _extract_array(obj):
        # TODO: remove delayed trip
        objs = obj.to_delayed()
        dtype = obj.dtype._record_type
        arrays = [da.from_delayed(x.array.data, shape=(np.nan,), dtype=dtype)
                  for x in objs]
        arr = da.concatenate(arrays)
        return IPArray(arr)

    @property
    def _constructor(self):
        return dd.Series
