import abc
import collections
import ipaddress
import operator

import six
import numpy as np
import pandas as pd
# TODO: public API
from pandas.core.arrays import ExtensionArray
from pandas.core.dtypes.dtypes import ExtensionDtype

from ._accessor import (DelegatedMethod, DelegatedProperty,
                        delegated_method)
from ._utils import combine, pack, unpack
from .common import _U8_MAX, _IPv4_MAX
from .parser import _to_ipaddress_pyint, _as_ip_object

# -----------------------------------------------------------------------------
# Extension Type
# -----------------------------------------------------------------------------


@six.add_metaclass(abc.ABCMeta)
class IPv4v6Base(object):
    """Metaclass providing a common base class for the two scalar IP types."""
    pass


IPv4v6Base.register(ipaddress.IPv4Address)
IPv4v6Base.register(ipaddress.IPv6Address)


class IPType(ExtensionDtype):
    name = 'ip'
    type = IPv4v6Base
    kind = 'O'
    _record_type = np.dtype([('hi', '>u8'), ('lo', '>u8')])
    na_value = ipaddress.IPv4Address(0)

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


class IPArray(ExtensionArray):
    """Holder for IP Addresses."""
    # A note on the internal data layout. IPv6 addresses require 128 bits,
    # which is more than a uint64 can store. So we use a NumPy structured array
    # with two fields, 'hi', 'lo' to store the data. Each field is a uint64.
    # The 'hi' field contains upper 64 bits. The think this is correct since
    # all IP traffic is big-endian.
    __array_priority__ = 1000
    _dtype = IPType()
    ndim = 1
    can_hold_na = True

    def __init__(self, values):
        from .parser import _to_ip_array

        values = _to_ip_array(values)  # TODO: avoid potential copy
        self.data = values

    @classmethod
    def _constructor_from_sequence(cls, scalars):
        return cls(scalars)

    # -------------------------------------------------------------------------
    # Pandas Interface
    # -------------------------------------------------------------------------
    @property
    def dtype(self):
        """The dtype for this extension array, IPType"""
        return self._dtype

    @property
    def shape(self):
        """A length-tuple with the length of the array."""
        return (len(self.data),)

    @property
    def nbytes(self):
        """The number of bytes taken to store this array.

        It takes 16 bytes to store each addresses.
        """
        return 16 * len(self)

    def take(self, indexer, allow_fill=True, fill_value=None):
        mask = indexer == -1
        result = self.data.take(indexer)
        result[mask] = unpack(pack(int(self.na_value)))
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
    def na_value(self):
        return self.dtype.na_value

    def to_pyipaddress(self):
        import ipaddress
        return [ipaddress.ip_address(x) for x in self._format_values()]

    def to_pyints(self):
        return [combine(*map(int, x)) for x in self.data]

    def to_bytes(self):
        """Serialize the IPArray as a Python bytestring.

        Examples
        --------
        >>> arr = IPArray([10, 20])
        >>> arr.to_bytes()
        b'\x00\x00\...x00\x02'
        """
        return self.data.tobytes()

    def __repr__(self):
        formatted = self._format_values()
        return "IPArray({!r})".format(formatted)

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
    def from_pyints(cls, values):
        # type: T.Sequence[int]) -> 'IPArray'
        return cls(_to_ipaddress_pyint(values))

    @classmethod
    def from_bytes(cls, bytestring):
        """Create an IPArray from a bytestring.

        Parameters
        ----------
        bytestring : bytes
            Note that bytestring is a Python 3-style string of bytes,
            not a sequences of bytes where each element represents an
            IPAddress.

        Returns
        -------
        IPArray

        Examples
        --------
        >>> arr = IPArray([10, 20])
        >>> buf = arr.to_bytes()
        >>> buf
        b'\x00\x00\...x00\x02'
        >>> IPArray.from_bytes(buf)
        IPArray(['0.0.0.10', '0.0.0.20'])

        See Also
        --------
        to_bytes
        from_pyints
        """
        data = np.frombuffer(bytestring, dtype=IPType._record_type)
        return cls._from_ndarray(data)

    @classmethod
    def _from_ndarray(cls, data, copy=False):
        """Zero-copy construction of an IPArray from an ndarray.

        Parameters
        ----------
        data : ndarray
            This should have IPType._record_type dtype
        copy : bool, default False
            Whether to copy the data.

        Returns
        -------
        ExtensionArray
        """
        if copy:
            data = data.copy()
        new = IPArray([])
        new.data = data
        return new

    def __eq__(self, other):
        # TDOO: scalar ipaddress
        if not isinstance(other, IPArray):
            return NotImplemented
        mask = self.isna() | other.isna()
        result = self.data == other.data
        result[mask] = False
        return result

    def __lt__(self, other):
        # TDOO: scalar ipaddress
        if not isinstance(other, IPArray):
            return NotImplemented
        mask = self.isna() | other.isna()
        result = ((self.data['hi'] <= other.data['hi']) &
                  (self.data['lo'] < other.data['lo']))
        result[mask] = False
        return result

    def __le__(self, other):
        if not isinstance(other, IPArray):
            return NotImplemented
        mask = self.isna() | other.isna()
        result = ((self.data['hi'] <= other.data['hi']) &
                  (self.data['lo'] <= other.data['lo']))
        result[mask] = False
        return result

    def __gt__(self, other):
        if not isinstance(other, IPArray):
            return NotImplemented
        return other < self

    def __ge__(self, other):
        if not isinstance(other, IPArray):
            return NotImplemented
        return other <= self

    def equals(self, other):
        if not isinstance(other, IPArray):
            raise TypeError("Cannot compare 'IPArray' "
                            "to type '{}'".format(type(other)))
        # TODO: missing
        return (self.data == other.data).all()

    def isna(self):
        ips = self.data
        return (ips['lo'] == 0) & (ips['lo'] - ips['hi'] == 0)

    def argsort(self, axis=-1, kind='quicksort', order=None):
        return self.data.argsort()

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
        """Check whether elements of 'self' are in 'other'.

        Comparison is done elementwise.

        Parameters
        ----------
        other : str or sequences
            For ``str`` 'other', the argument is attempted to
            be converted to an :class:`ipaddress.IPv4Network` or
            a :class:`ipaddress.IPv6Network` or an :class:`IPArray`.
            If all those conversions fail, a TypeError is raised.

            For a sequence of strings, the same conversion is attempted.
            You should not mix networks with addresses.

            Finally, other may be an ``IPArray`` of addresses to compare to.

        Returns
        -------
        contained : ndarray
            A 1-D boolean ndarray with the same length as self.

        Examples
        --------
        Comparison to a single network

        >>> s = IPArray(['192.168.1.1', '255.255.255.255'])
        >>> s.isin('192.168.1.0/24')
        array([ True, False])

        Comparison to many networks
        >>> s.isin(['192.168.1.0/24', '192.168.2.0/24'])
        array([ True, False])

        Comparison to many IP Addresses

        >>> s.isin(['192.168.1.1', '192.168.1.2', '255.255.255.1']])
        array([ True, False])
        """
        box = (isinstance(other, str) or
               not isinstance(other, (IPArray, collections.Sequence)))
        if box:
            other = [other]

        networks = []
        addresses = []

        if not isinstance(other, IPArray):
            for net in other:
                net = _as_ip_object(net)
                if isinstance(net, (ipaddress.IPv4Network,
                                    ipaddress.IPv6Network)):
                    networks.append(net)
                if isinstance(net, (ipaddress.IPv4Address,
                                    ipaddress.IPv6Address)):
                    addresses.append(ipaddress.IPv6Network(net))
        else:
            addresses = other

        # Flatten all the addresses
        addresses = IPArray(addresses)  # TODO: think about copy=False

        mask = np.zeros(len(self), dtype='bool')
        for network in networks:
            mask |= self._isin_network(network)

        # no... we should flatten this.
        mask |= self._isin_addresses(addresses)
        return mask

    def _isin_network(self, other):
        # type: (Union[ipaddress.IPv4Network,ipaddress.IPv6Network]) -> ndarray
        """Check whether an array of addresses is contained in a network."""
        # A network is bounded below by 'network_address' and
        # above by 'broadcast_address'.
        # IPArray handles comparisons between arrays of addresses, and NumPy
        # handles broadcasting.
        net_lo = type(self)([other.network_address])
        net_hi = type(self)([other.broadcast_address])

        return (net_lo <= self) & (self <= net_hi)

    def _isin_addresses(self, other):
        """Check whether elements of self are present in other."""
        from pandas.core.algorithms import isin
        # TODO(factorize): replace this
        return isin(self, other)

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
        # https://github.com/pandas-dev/pandas/pull/19869
        _, indices = np.unique(self.data, return_index=True)
        data = self.data.take(np.sort(indices))
        return self._from_ndarray(data)

    def factorize(self, na_sentinel):
        # XXX: Verify this, check for better algo
        # XXX: This is broken for NA values...
        uniques, indices, labels = np.unique(self.data,
                                             return_index=True,
                                             return_inverse=True)
        return labels, uniques


# -----
# Index
# -----

class IPAddressIndex(pd.Index):
    _typ = 'ipaddressindex'
    _attributes = ['name']
    _holder = IPArray

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

@pd.api.extensions.register_series_accessor("ip")
class IPAccessor:

    is_ipv4 = DelegatedProperty("is_ipv4")
    is_ipv6 = DelegatedProperty("is_ipv6")
    version = DelegatedProperty("version")
    is_multicast = DelegatedProperty("is_multicast")
    is_private = DelegatedProperty("is_private")
    is_global = DelegatedProperty("is_global")
    is_unspecified = DelegatedProperty("is_unspecified")
    is_reserved = DelegatedProperty("is_reserved")
    is_loopback = DelegatedProperty("is_loopback")
    is_link_local = DelegatedProperty("is_link_local")

    isna = DelegatedMethod("isna")
    to_pyints = DelegatedMethod("to_pyints")

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
        return delegated_method(self._data.isin, self._index,
                                self._name, other)


def is_ipaddress_type(obj):
    t = getattr(obj, 'dtype', obj)
    try:
        return isinstance(t, IPType) or issubclass(t, IPType)
    except Exception:
        return False
