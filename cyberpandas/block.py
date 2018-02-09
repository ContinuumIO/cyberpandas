import abc
import collections
import ipaddress
import operator
import typing as T

import numpy as np
import pandas as pd
# TODO: public API
from pandas.core.arrays import ExtensionArray
from pandas.core.dtypes.dtypes import ExtensionDtype

from .common import _U8_MAX, _IPv4_MAX
from .parser import _to_ipaddress_pyint

# -----------------------------------------------------------------------------
# Extension Type
# -----------------------------------------------------------------------------


class IPv4v6Base(metaclass=abc.ABCMeta):
    pass


IPv4v6Base.register(ipaddress.IPv4Address)
IPv4v6Base.register(ipaddress.IPv6Address)


class IPType(ExtensionDtype):
    name = 'ip'
    type = IPv4v6Base
    kind = 'O'
    mybase = np.dtype([('hi', '>u8'), ('lo', '>u8')])
    fill_value = ipaddress.IPv4Address(0)

    @classmethod
    def construct_from_string(cls, string):
        if string == cls.name:
            return cls()
        else:
            raise TypeError("Cannot construct a '{}' from "
                            "'{}'".format(cls, string))

# -----------------------------------------------------------------------------
# Extension Container
# -----------------------------------------------------------------------------


class IPAddress(ExtensionArray):
    """Holder for things"""
    # A note on the internal data layout. IPv6 addresses require 128 bits,
    # which is more than a uint64 can store. So we use a NumPy structured array
    # with two fields, 'hi', 'lo' to store the data. Each field is a uint64.
    # The 'hi' field contains upper 64 bits. The think this is correct since
    # all IP traffic is big-endian.
    __array_priority__ = 1000
    _dtype = IPType()
    _typ = 'ip'
    ndim = 1
    can_hold_na = True

    def __init__(self, values):
        from .parser import _to_ip_array

        values = _to_ip_array(values)  # TODO: avoid potential copy
        self.data = values

    # -------------------------------------------------------------------------
    # Pandas Interface
    # -------------------------------------------------------------------------
    @property
    def dtype(self):
        return self._dtype

    @property
    def shape(self):
        return (len(self.data),)

    @property
    def nbytes(self):
        return 2 * 64 * len(self)

    def view(self, dtype=None):
        return self.data.view()

    def take(self, indexer, allow_fill=True, fill_value=None):
        mask = indexer == -1
        result = self.data.take(indexer)
        result[mask] = self._fill_value
        return type(self)(result)

    def _formatting_values(self):
        return np.array(self._format_values(), dtype='object')

    @classmethod
    def _concat_same_type(cls, to_concat):
        return cls(np.concatenate([array.data for array in to_concat]))

    def take_nd(self, indexer, allow_fill=True, fill_value=None):
        return self.take(indexer, allow_fill=allow_fill, fill_value=fill_value)

    def copy(self, deep=False):
        return type(self)(self.data.copy())

    # -------------------------------------------------------------------------
    # Iterator / Sequence interface
    # -------------------------------------------------------------------------
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

    def __setitem__(self, key, value):
        from .parser import to_ipaddress

        value = to_ipaddress(value).data
        self.data[key] = value

    def __iter__(self):
        return iter(self.to_pyipaddress())

    @property
    def _fill_value(self):
        return self.dtype.fill_value

    def to_pyipaddress(self):
        import ipaddress
        return [ipaddress.ip_address(x) for x in self._format_values()]

    def to_pyints(self):
        from .parser import combine
        return [combine(*map(int, x)) for x in self.data]

    def __repr__(self):
        formatted = self._format_values()
        return "IPAddress({!r})".format(formatted)

    def _format_values(self):
        formatted = []
        # TODO: perf
        for i in range(len(self)):
            hi, lo = self.data[i]
            if lo == -1:
                formatted.append("NA")
            elif hi == 0 and lo <= _IPv4_MAX:
                formatted.append(ipaddress.IPv4Address._string_from_ip_int(
                    int(lo)))
            elif hi == 0:
                formatted.append(ipaddress.IPv6Address._string_from_ip_int(
                    int(lo)))
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
        # TDOO: scalar ipaddress
        if not isinstance(other, IPAddress):
            return NotImplemented
        mask = self.isna() | other.isna()
        result = self.data == other.data
        result[mask] = False
        return result

    def __lt__(self, other):
        # TDOO: scalar ipaddress
        if not isinstance(other, IPAddress):
            return NotImplemented
        mask = self.isna() | other.isna()
        result = ((self.data['hi'] <= other.data['hi']) &
                  (self.data['lo'] < other.data['lo']))
        result[mask] = False
        return result

    def __le__(self, other):
        if not isinstance(other, IPAddress):
            return NotImplemented
        mask = self.isna() | other.isna()
        result = ((self.data['hi'] <= other.data['hi']) &
                  (self.data['lo'] <= other.data['lo']))
        result[mask] = False
        return result

    def __gt__(self, other):
        if not isinstance(other, IPAddress):
            return NotImplemented
        return other < self

    def __ge__(self, other):
        if not isinstance(other, IPAddress):
            return NotImplemented
        return other <= self

    def equals(self, other):
        if not isinstance(other, IPAddress):
            raise TypeError("Cannot compare 'IPAddress' "
                            "to type '{}'".format(type(other)))
        # TODO: missing
        return (self.data == other.data).all()

    def isna(self):
        ips = self.data
        return ips['lo'] - ips['hi'] == 0

    @property
    def is_ipv4(self):
        # TODO: NA should be NA
        ips = self.data
        return (ips['hi'] == 0) & (ips['lo'] < _U8_MAX)

    @property
    def is_ipv6(self):
        ips = self.data
        return (ips['hi'] > 0) | (ips['lo'] > _U8_MAX)

    @property
    def version(self):
        return np.where(self.is_ipv4, 4, 6)

    @property
    def is_multicast(self):
        pyips = self.to_pyipaddress()
        return np.array([ip.is_multicast for ip in pyips])

    @property
    def is_private(self):
        pyips = self.to_pyipaddress()
        return np.array([ip.is_private for ip in pyips])

    @property
    def is_global(self):
        pyips = self.to_pyipaddress()
        return np.array([ip.is_global for ip in pyips])

    @property
    def is_unspecified(self):
        pyips = self.to_pyipaddress()
        return np.array([ip.is_unspecified for ip in pyips])

    @property
    def is_reserved(self):
        pyips = self.to_pyipaddress()
        return np.array([ip.is_reserved for ip in pyips])

    @property
    def is_loopback(self):
        pyips = self.to_pyipaddress()
        return np.array([ip.is_loopback for ip in pyips])

    @property
    def is_link_local(self):
        pyips = self.to_pyipaddress()
        return np.array([ip.is_link_local for ip in pyips])

    @property
    def packed(self):
        """Bytestring of the IP addresses

        Each address takes 16 bytes. IPv4 addresses are prefixed
        by zeros.
        """
        # TODO: I wonder if that should be post-fixed by 0s.
        return self.data.tobytes()

    def isin(self, other):
        """

        Examples
        --------
        >>> s = IPAddress(['192.168.1.1', '255.255.255.255'])
        >>> s.isin('192.168.1.0/24')
        array([ True, False])
        """
        if isinstance(other, str) or not isinstance(other,
                                                    collections.Sequence):
            other = [other]

        networks = []
        for net in other:
            try:
                networks.append(ipaddress.IPv4Network(net))
            except ValueError:
                networks.append(ipaddress.IPv6Network(net))

        # TODO: perf
        pyips = self.to_pyipaddress()
        mask = np.zeros(len(self), dtype='bool')
        for network in networks:
            for i, ip in enumerate(pyips):
                if ip in network:
                    mask[i] = True
        return mask

    def setitem(self, indexer, value):
        """Set the 'value' inplace.
        """
        # I think having a separate than __setitem__ is good
        # since we have to return here, but __setitem__ doesn't.
        self[indexer] = value
        return self

    @property
    def index_type(self):
        return IPAddressIndex

    def unique(self):
        # type: () -> ExtensionArray
        pass

    def factorize(self):
        # XXX: Verify this, check for better algo
        # astype to avoid endianness issues in pd.factorize
        a, _ = pd.factorize(self.data['lo'].astype('u8'))
        b, _ = pd.factorize(self.data['hi'].astype('u8'))

        labels = np.bitwise_xor.reduce(
            np.concatenate([a.reshape(-1, 1),
                            b.reshape(-1, 1)], axis=1),
            axis=1
        )

        # TODO: refactor into a .unique
        # TODO: Handle empty, scalar, etc.
        mask = np.zeros(len(labels), dtype=bool)
        mask[0] = True
        inner_mask = (labels[1:] - labels[:-1]) != 0
        mask[1:] = inner_mask

        uniques = self[mask]
        return labels, uniques


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
# Accessor
# -----------------------------------------------------------------------------


class _Delegated:

    def __init__(self, name):
        self.name = name

    def __get__(self, obj, type=None):
        index = object.__getattribute__(obj, '_index')
        name = object.__getattribute__(obj, '_name')
        result = self._get_result(obj)
        return pd.Series(result, index, name)


class _DelegatedProperty(_Delegated):
    def _get_result(self, obj, type=None):
        return getattr(object.__getattribute__(obj, '_data'), self.name)


class _DelegatedMethod(_Delegated):
    def __get__(self, obj, type=None):
        index = object.__getattribute__(obj, '_index')
        name = object.__getattribute__(obj, '_name')
        method = getattr(object.__getattribute__(obj, '_data'), self.name)
        return _delegated_method(method, index, name)


def _delegated_method(method, index, name, *args, **kwargs):
    return pd.Series(method(*args, **kwargs), index, name)


@pd.api.extensions.register_series_accessor("ip")
class IPAccessor:

    is_ipv4 = _DelegatedProperty("is_ipv4")
    is_ipv6 = _DelegatedProperty("is_ipv6")
    version = _DelegatedProperty("version")
    is_multicast = _DelegatedProperty("is_multicast")
    is_private = _DelegatedProperty("is_private")
    is_global = _DelegatedProperty("is_global")
    is_unspecified = _DelegatedProperty("is_unspecified")
    is_reserved = _DelegatedProperty("is_reserved")
    is_loopback = _DelegatedProperty("is_loopback")
    is_link_local = _DelegatedProperty("is_link_local")

    isna = _DelegatedMethod("isna")
    to_pyints = _DelegatedMethod("to_pyints")

    def __init__(self, obj):
        self._validate(obj)
        self._data = obj.values
        self._index = obj.index
        self._name = obj.name

    @staticmethod
    def _validate(obj):
        if not is_ipaddress_type(obj):
            raise AttributeError("Cannot use 'ip' accessor on objects of "
                                 "dtype '{}'.".format(obj.dtype))

    def isin(self, other):
        return _delegated_method(self._data.isin, self._index,
                                 self._name, other)


def is_ipaddress_type(obj):
    t = getattr(obj, 'dtype', obj)
    try:
        return isinstance(t, IPType) or issubclass(t, IPType)
    except Exception:
        return False
