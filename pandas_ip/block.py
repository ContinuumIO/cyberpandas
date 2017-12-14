import struct
import ipaddress

import numpy as np
import pandas as pd
from pandas.core.internals import NonConsolidatableMixIn, Block
from pandas.core.dtypes.dtypes import ExtensionDtype

import typing as T


_IPv4_MAX = 2 ** 32 - 1
_IPv6_MAX = 2 ** 128 - 1
_U8_MAX = 2 ** 64 - 1

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
    base = np.dtype([('lo', '>u8'), ('hi', '>u8')])


# -----------------------------------------------------------------------------
# Extnesion Container
# -----------------------------------------------------------------------------


class IPAddress:
    """Holder for things"""
    __array_priority__ = 1000
    _dtype = IPType
    _typ = 'ip'
    ndim = 1

    def __init__(self, values, meta=None):
        # TODO: raise if they pass values like [1, 2, 3]?
        # That's currently interpreted as [(1, 1), (2, 2), (3, 3)].
        self.ips = np.asarray(values, dtype=self.dtype.base)

    def __array__(self, values):
        return self.ips

    def __repr__(self):
        formatted = self._format_values()
        return "<IPAddress({!r})>".format(formatted)

    def _format_values(self):
        formatted = []
        # TODO: perf
        for i in range(len(self)):
            lo, hi = self.ips[i]
            if lo == -1:
                formatted.append("NA")
            elif lo == 0:
                formatted.append(ipaddress.IPv4Address._string_from_ip_int(
                    int(hi)))
            else:
                # TODO:
                formatted.append(ipaddress.IPv6Address._string_from_ip_int(
                    (int(hi) << 64) + int(lo)))
        return formatted

    def __len__(self):
        return len(self.ips)

    def tolist(self):
        return self.ips.tolist()

    def view(self):
        return self.ips.view()

    @classmethod
    def from_pyints(cls, values: T.Sequence[int]) -> 'IPAddress':
        return _to_ipaddress_pyint(values)

    @property
    def dtype(self):
        return self._dtype

    @property
    def shape(self):
        return (len(self.ips),)

    @property
    def is_na(self):
        # Assuming we use 0.0.0.0 for N/A
        ips = self.ips
        # XXX: this could overflow uint64...
        return ips['lo'] + ips['hi'] == 0

    @property
    def is_ipv4(self):
        # TODO: NA should be NA
        ips = self.ips
        return (ips['lo'] == 0) & (ips['hi'] < _U8_MAX)

    @property
    def is_ipv6(self):
        ips = self.ips
        return (ips['lo'] == 1) | (ips['hi'] > _U8_MAX)


# -----------------------------------------------------------------------------
# Utilities
# -----------------------------------------------------------------------------


def pack(ip: int) -> bytes:
    return ip.to_bytes(16, 'big')


def unpack(ip: bytes) -> T.Tuple[int, int]:
    # Recipe 3.5 from Python Cookbook 3rd ed. (p. 90)
    # int.from_bytes(data, 'big') for Py3+
    hi, lo = struct.unpack(">QQ", ip)
    return hi, lo


def combine(hi: int, lo: int) -> int:
    """Combine the hi and lo bytes into the final ip address."""
    return (hi << 64) + lo


def to_ipaddress(values):
    pass


def _to_ipaddress_str(values):
    pass


def _to_ipaddress_pyint(values):
    values2 = (unpack(pack(x)) for x in values)
    return IPAddress(list(values2))


def _to_ipaddress_bytes(values):
    pass


# -----------------------------------------------------------------------------
# Extension Block
# -----------------------------------------------------------------------------


class IPBlock(NonConsolidatableMixIn, Block):
    """Block type for IP Address dtype

    Notes
    -----
    This can hold either IPv4 or IPv6 addresses.

    """
    _holder = IPAddress

    def __init__(self, values, placement, ndim=None, fastpath=False):
        if not isinstance(values, self._holder):
            values = IPAddress(values)
        super().__init__(values, placement, ndim=ndim, fastpath=fastpath)

    def formatting_values(self):
        return np.array(self.values._format_values(), dtype='object')

    def concat_same_type(self, to_concat, placement=None):
        values = np.concatenate([blk.values.ips for blk in to_concat])
        return self.make_block_same_class(
            values, placement=placement or slice(0, len(values), 1)
        )


# -----------------------------------------------------------------------------
# Accessor
# -----------------------------------------------------------------------------


class IPAccessor:

    def __init__(self, obj):
        self._data = obj.values
        self._index = obj.index
        self._name = obj.name

    @classmethod
    def _make_accessor(cls, data):
        return cls(data.values, data.index, getattr(data, 'name', None))

    @property
    def is_na(self):
        # Assuming we use 0.0.0.0 for N/A
        return pd.Series(self._data.is_na, self._index, name=self._name)

    @property
    def is_ipv4(self):
        # TODO: NA should be NA
        return pd.Series(self._data.is_ipv4, self._index, name=self._name)

    @property
    def is_ipv6(self):
        return pd.Series(self._data.is_ipv6, self._index, name=self._name)


pd.register_series_accessor("ip")(IPAccessor)  # decorate
