import ipaddress

import numpy as np
import pandas as pd
from pandas.core.internals import NonConsolidatableMixIn, Block
from pandas.core.dtypes.dtypes import ExtensionDtype
from pandas.core.accessor import PandasDelegate, AccessorProperty


IPv4_MAX = 2 ** 32 - 1
IPv6_MAX = 2 ** 128 - 1

# -----------------------------------------------------------------------------
# Extension Type
# -----------------------------------------------------------------------------


class IPTypeType(type):
    pass


class IPType(ExtensionDtype):
    name = 'ip'
    type = IPTypeType
    kind = 'O'
    str = '|O08'
    base = np.dtype('O')


# -----------------------------------------------------------------------------
# Extnesion Container
# -----------------------------------------------------------------------------


class IP:
    """Holder for things"""
    __array_priority__ = 1000
    _dtype = IPType
    _typ = 'ip'
    ndim = 1

    def __init__(self, values, meta=None):
        self.ips = np.asarray(values)
        if meta is None:
            self._meta = infer_meta(self.ips)
        else:
            self._meta = meta

    def __array__(self, values):
        return self.ips

    def __repr__(self):
        formatted = self._format_values()
        return "<IPAddress({!r})>".format(formatted)

    def _format_values(self):
        formatted = []
        # TODO: perf
        for i in range(len(self)):
            if self._meta[i] == 0:
                formatted.append("NA")
            elif self._meta[i] == 1:
                formatted.append(ipaddress.IPv4Address._string_from_ip_int(
                    int(self.ips[i])))
            else:
                formatted.append(ipaddress.IPv6Address._string_from_ip_int(
                    int(self.ips[i])))
        return formatted

    def __len__(self):
        return len(self.ips)

    def tolist(self):
        return self.ips.tolist()

    def view(self):
        return self.ips.view()

    @property
    def dtype(self):
        return self._dtype


def infer_meta(values):
    """Infer metadata about an array of IP addresses.

    Metadata is stored as a uint8 where

    - 0 indicates null
    - 1 indicates IPv4
    - 2 indicates IPv6
    """
    meta = np.ones(len(values), dtype=np.uint8)
    meta[values > IPv4_MAX] = 2

    return meta


# -----------------------------------------------------------------------------
# Extension Block
# -----------------------------------------------------------------------------


class IPBlock(NonConsolidatableMixIn, Block):
    """Block type for IP Address dtype

    Notes
    -----
    This can hold either IPv4 or IPv6 addresses.

    """
    _holder = IP

    def formatting_values(self):
        return np.array(self.values._format_values(), dtype='object')

    def concat_same_type(self, to_concat, placement=None):
        pass


# -----------------------------------------------------------------------------
# Accessor
# -----------------------------------------------------------------------------


class IPAccessor(PandasDelegate):

    def __init__(self, values, index, name):
        self._data = values
        self._index = index
        self._name = name

    @classmethod
    def _make_accessor(cls, data):
        return IPAccessor(data.values, data.index, getattr(data, 'name', None))

    @property
    def is_na(self):
        return pd.Series(self._data._meta == 0, self._index, name=self._name)

    @property
    def is_ipv4(self):
        # TODO: NA should be NA
        return pd.Series(self._data._meta == 1, self._index, name=self._name)

    @property
    def is_ipv6(self):
        return pd.Series(self._data._meta == 2, self._index, name=self._name)


def patch():
    pd.Series.ip = AccessorProperty(IPAccessor)
    pd.DataFrame.ip = AccessorProperty(IPAccessor)
