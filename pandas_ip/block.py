import ipaddress
import operator

import numpy as np
import pandas as pd
from pandas.core.internals import NonConsolidatableMixIn, Block
from pandas.core.dtypes.dtypes import ExtensionDtype
from pandas.core.extension import ExtensionArray
from pandas.core.common import is_null_slice

import typing as T

from .parser import _to_ipaddress_pyint
from .common import _U8_MAX

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
# Extension Container
# -----------------------------------------------------------------------------


class IPAddress(ExtensionArray):
    """Holder for things"""
    __array_priority__ = 1000
    _dtype = IPType
    _typ = 'ip'
    ndim = 1

    def __init__(self, values, meta=None):
        from .parser import _to_ip_array

        values = _to_ip_array(values)  # TODO: avoid potential copy
        self.data = values

    # Pandas Interface
    def __array__(self, dtype=None):
        return np.array(self.data, dtype=dtype)

    @property
    def dtype(self):
        return self._dtype

    @property
    def shape(self):
        return (len(self.data),)

    @property
    def _block_type(self):
        return IPBlock

    @property
    def nbytes(self):
        return 2 * 64 * len(self)

    def view(self, dtype=None):
        return self.data.view()

    def take(self, indexer, allow_fill=True, fill_value=None):
        # XXX: NA-fill
        mask = indexer == -1
        result = self.data.take(indexer)
        result[mask] = self._fill_value
        return type(self)(result)

    def take_nd(self, indexer, allow_fill=True, fill_value=None):
        return self.take(indexer, allow_fill=allow_fill, fill_value=fill_value)

    def copy(self, deep=False):
        return type(self)(self.data.copy())

    # Iterator / Sequence interfae
    def __len__(self):
        return len(self.data)

    def __getitem__(self, *args):
        from .parser import combine

        result = operator.getitem(self.data, *args)
        if isinstance(result, tuple):
            return ipaddress.ip_address(combine(*result))
        elif isinstance(result, np.void):
            result = result.item()
            return ipaddress.ip_address(combine(*result))
        else:
            return type(self)(result)

    def __iter__(self):
        return iter(self.data)

    @property
    def _fill_value(self):
        return np.array((0, 0), dtype=self.dtype.base)

    # Utility methods
    def to_series(self, index=None, name=None):
        n = len(self)
        placement = slice(n)
        block = self._block_type(self, placement=placement)
        if index is None:
            index = pd.RangeIndex(n)
        return pd.Series(block, index=index, name=name, fastpath=True)

    def to_pyipaddress(self):
        import ipaddress
        return [ipaddress.ip_address(x) for x in self._format_values()]

    def __repr__(self):
        formatted = self._format_values()
        return "<IPAddress({!r})>".format(formatted)

    def _format_values(self):
        formatted = []
        # TODO: perf
        for i in range(len(self)):
            lo, hi = self.data[i]
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

    def tolist(self):
        return self.data.tolist()

    @classmethod
    def from_pyints(cls, values: T.Sequence[int]) -> 'IPAddress':
        return cls(_to_ipaddress_pyint(values))

    def __eq__(self, other):
        if not isinstance(other, IPAddress):
            return NotImplemented
        return self.data == other.data

    def equals(self, other):
        if not isinstance(other, IPAddress):
            raise TypeError
        return (self.data == other.data).all()

    def isna(self):
        # Assuming we use 0.0.0.0 for N/A
        ips = self.data
        # XXX: this could overflow uint64...
        return ips['lo'] + ips['hi'] == 0

    @property
    def is_ipv4(self):
        # TODO: NA should be NA
        ips = self.data
        return (ips['lo'] == 0) & (ips['hi'] < _U8_MAX)

    @property
    def is_ipv6(self):
        ips = self.data
        return (ips['lo'] > 0) | (ips['hi'] > _U8_MAX)

    @property
    def packed(self):
        """Bytestring of the IP addresses

        Each address takes 16 bytes. IPv4 addresses are prefixed
        by zeros.
        """
        # TODO: I wonder if that should be post-fixed by 0s.
        return self.data.tobytes()

    def value_counts(self, normalize=False, sort=True, ascending=False,
                     bins=None, dropna=True):
        from pandas.core.algorithms import value_counts
        counts = value_counts(self.data, sort=sort, normalize=normalize,
                              ascending=ascending, bins=bins, dropna=dropna)
        counts.index = IPAddressIndex(counts.index)
        return counts


# -----
# Index
# -----

class IPAddressIndex(pd.Index):
    _typ = 'ipaddressindex'
    _attributes = ['name']
    _holder = IPAddress

    def __new__(cls, data=None, name=None):
        from .parser import _to_ip_array

        if data is None:
            data = []

        data = _to_ip_array(data)
        return cls._simple_new(data, name=name)

    @classmethod
    def _simple_new(cls, data, name=None):
        result = object.__new__(cls)
        values = cls._holder(data)
        result._data = values
        result._name = name
        result._reset_identity()
        return result

    def __repr__(self):
        tpl = 'IPAddressIndex({})'
        return tpl.format(self._data._format_values())

    @property
    def inferred_type(self):
        return self._typ

    @property
    def values(self):
        return self._data

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
        values = np.concatenate([blk.values.data for blk in to_concat])
        return self.make_block_same_class(
            values, placement=placement or slice(0, len(values), 1)
        )

    def _slice(self, slicer):
        """ Return a slice of myself.

        For internal compatibility with numpy arrays.
        """
        # XXX: Would like to handle this better...
        # We're forced to handle 2-d slicing by the BlockMananger,
        # even though we're only ever 1-d
        # only allow 1 dimensional slicing, but can
        # in a 2-d case be passd (slice(None),....)
        if isinstance(slicer, tuple) and len(slicer) == 2:
            if not is_null_slice(slicer[0]):
                raise AssertionError("invalid slicing for a 1-ndim "
                                     "categorical")
            slicer = slicer[1]

        return self.values[slicer]

    def get_values(self, dtype=None):
        return self.values.data.astype(object)

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
    def is_ipv4(self):
        # TODO: NA should be NA
        return pd.Series(self._data.is_ipv4, self._index, name=self._name)

    @property
    def is_ipv6(self):
        return pd.Series(self._data.is_ipv6, self._index, name=self._name)

    def isna(self):
        # Assuming we use 0.0.0.0 for N/A
        return pd.Series(self._data.isna(), self._index, name=self._name)

    @property
    def packed(self):
        return pd.Series(self._data.packed, self._index, name=self._name)

    @property
    def is_multicast(self):
        pass


pd.api.extensions.register_series_accessor("ip")(IPAccessor)  # decorate
