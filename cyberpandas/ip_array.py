import abc
import collections
import ipaddress

import six
import numpy as np
import pandas as pd
from pandas.api.extensions import ExtensionDtype

from ._accessor import (DelegatedMethod, DelegatedProperty,
                        delegated_method)
from ._utils import combine, pack, unpack
from .base import NumPyBackedExtensionArrayMixin
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


class IPArray(NumPyBackedExtensionArrayMixin):
    """Holder for IP Addresses.

    IPArray is a container for IPv4 or IPv6 addresses. It satisfies pandas'
    extension array interface, and so can be stored inside
    :class:`pandas.Series` and :class:`pandas.DataFrame`.

    See :ref:`usage` for more.
    """
    # A note on the internal data layout. IPv6 addresses require 128 bits,
    # which is more than a uint64 can store. So we use a NumPy structured array
    # with two fields, 'hi', 'lo' to store the data. Each field is a uint64.
    # The 'hi' field contains upper 64 bits. The think this is correct since
    # all IP traffic is big-endian.
    __array_priority__ = 1000
    _dtype = IPType()
    _itemsize = 16
    ndim = 1
    can_hold_na = True

    def __init__(self, values):
        from .parser import _to_ip_array

        values = _to_ip_array(values)  # TODO: avoid potential copy
        self.data = values

    @classmethod
    def from_pyints(cls, values):
        # type: (T.Sequence[int]) -> 'IPArray'
        """Construct an IPArray from a sequence of Python integers.

        This can be useful for representing IPv6 addresses, which may
        be larger than 2**64.

        Parameters
        ----------
        values : Sequence
            Sequence of Python integers.

        Examples
        --------
        >>> IPArray.from_pyints([0, 10, 2 ** 64 + 1])
        IPArray(['0.0.0.1', '0.0.0.2', '0.0.0.3', '0:0:0:1::'])
        """
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

    # -------------------------------------------------------------------------
    # Properties
    # -------------------------------------------------------------------------
    @property
    def na_value(self):
        """The missing value sentinal for IP Addresses.

        The address ``'0.0.0.0'`` is used.

        Examples
        --------
        >>> IPArray([]).na_value
        IPv4Address('0.0.0.0')
        """
        return self.dtype.na_value

    def take(self, indices, allow_fill=False, fill_value=None):
        # Can't use pandas' take yet
        # 1. axis
        # 2. I don't know how to do the reshaping correctly.
        indices = np.asarray(indices, dtype='int')

        if allow_fill and fill_value is None:
            fill_value = unpack(pack(int(self.na_value)))
        elif allow_fill and not isinstance(fill_value, tuple):
            fill_value = unpack(pack(int(fill_value)))

        if allow_fill:
            mask = (indices == -1)
            if not len(self):
                if not (indices == -1).all():
                    msg = "Invalid take for empty array. Must be all -1."
                    raise IndexError(msg)
                else:
                    # all NA take from and empty array
                    took = (np.full((len(indices), 2), fill_value, dtype='>u8')
                              .reshape(-1).astype(self.dtype._record_type))
                    return self._from_ndarray(took)
            if (indices < -1).any():
                msg = ("Invalid value in 'indicies'. Must be all >= -1 "
                       "for 'allow_fill=True'")
                raise ValueError(msg)

        took = self.data.take(indices)
        if allow_fill:
            took[mask] = fill_value

        return self._from_ndarray(took)

    # -------------------------------------------------------------------------
    # Interfaces
    # -------------------------------------------------------------------------

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

    @staticmethod
    def _box_scalar(scalar):
        return ipaddress.ip_address(combine(*scalar))

    @property
    def _parser(self):
        from .parser import to_ipaddress
        return to_ipaddress

    def __setitem__(self, key, value):
        from .parser import to_ipaddress

        value = to_ipaddress(value).data
        self.data[key] = value

    def __iter__(self):
        return iter(self.to_pyipaddress())

    # ------------------------------------------------------------------------
    # Serializaiton / Export
    # ------------------------------------------------------------------------

    def to_pyipaddress(self):
        """Convert the array to a list of scalar IP Adress objects.

        Returns
        -------
        addresses : List
            Each element of the list will be an :class:`ipaddress.IPv4Address`
            or :class:`ipaddress.IPv6Address`, depending on the size of that
            element.

        See Also
        --------
        IPArray.to_pyints

        Examples
        ---------
        >>> IPArray(['192.168.1.1', '2001:db8::1000']).to_pyipaddress()
        [IPv4Address('192.168.1.1'), IPv6Address('2001:db8::1000')]
        """
        import ipaddress
        return [ipaddress.ip_address(x) for x in self._format_values()]

    def to_pyints(self):
        """Convert the array to a list of Python integers.

        Returns
        -------
        addresses : List[int]
            These will be Python integers (not NumPy), which are unbounded in
            size.

        See Also
        --------
        IPArray.to_pyipaddresses
        IPArray.from_pyints

        Examples
        --------
        >>> IPArray(['192.168.1.1', '2001:db8::1000']).to_pyints()
        [3232235777, 42540766411282592856903984951653830656]
        """
        return [combine(*map(int, x)) for x in self.data]

    def to_bytes(self):
        """Serialize the IPArray as a Python bytestring.

        This and :meth:IPArray.from_bytes is the fastest way to roundtrip
        serialize and de-serialize an IPArray.

        See Also
        --------
        IPArray.from_bytes

        Examples
        --------
        >>> arr = IPArray([10, 20])
        >>> arr.to_bytes()
        b'\x00\x00\...x00\x02'
        """
        return self.data.tobytes()

    # ------------------------------------------------------------------------
    # Ops
    # ------------------------------------------------------------------------

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

    def _values_for_factorize(self):
        return self.astype(object), ipaddress.IPv4Address(0)

    def isna(self):
        """Indicator for whether each element is missing.

        The IPAddress 0 is used to indecate missing values.

        Examples
        --------
        >>> IPArray(['0.0.0.0', '192.168.1.1']).isna()
        array([ True, False])
        """
        ips = self.data
        return (ips['lo'] == 0) & (ips['hi'] == 0)

    def isin(self, other):
        """Check whether elements of `self` are in `other`.

        Comparison is done elementwise.

        Parameters
        ----------
        other : str or sequences
            For ``str`` `other`, the argument is attempted to
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

    # ------------------------------------------------------------------------
    # IP Specific
    # ------------------------------------------------------------------------

    @property
    def is_ipv4(self):
        """Indicator for whether each address fits in the IPv4 space."""
        # TODO: NA should be NA
        ips = self.data
        return (ips['hi'] == 0) & (ips['lo'] < _U8_MAX)

    @property
    def is_ipv6(self):
        """Indicator for whether each address requires IPv6."""
        ips = self.data
        return (ips['hi'] > 0) | (ips['lo'] > _U8_MAX)

    @property
    def version(self):
        """IP version (4 or 6)."""
        return np.where(self.is_ipv4, 4, 6)

    @property
    def is_multicast(self):
        """Indiciator for whether each address is multicast."""
        pyips = self.to_pyipaddress()
        return np.array([ip.is_multicast for ip in pyips])

    @property
    def is_private(self):
        """Indiciator for whether each address is private."""
        pyips = self.to_pyipaddress()
        return np.array([ip.is_private for ip in pyips])

    @property
    def is_global(self):
        """Indiciator for whether each address is global."""
        pyips = self.to_pyipaddress()
        return np.array([ip.is_global for ip in pyips])

    @property
    def is_unspecified(self):
        """Indiciator for whether each address is unspecified."""
        pyips = self.to_pyipaddress()
        return np.array([ip.is_unspecified for ip in pyips])

    @property
    def is_reserved(self):
        """Indiciator for whether each address is reserved."""
        pyips = self.to_pyipaddress()
        return np.array([ip.is_reserved for ip in pyips])

    @property
    def is_loopback(self):
        """Indiciator for whether each address is loopback."""
        pyips = self.to_pyipaddress()
        return np.array([ip.is_loopback for ip in pyips])

    @property
    def is_link_local(self):
        """Indiciator for whether each address is link local."""
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
