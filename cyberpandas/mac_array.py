from collections import Iterable

import numpy as np
import six

from pandas.core.dtypes.dtypes import ExtensionDtype

from .base import NumPyBackedExtensionArrayMixin


class MACType(ExtensionDtype):
    """Dtype for MAC Address Data."""
    name = 'mac'
    # type is long for Py2 and int for py3
    type = six.integer_types[-1]
    kind = 'u'
    na_value = 0  # TODO: Check this.

    @classmethod
    def construct_from_string(cls, string):
        if string == cls.name:
            return cls()
        else:
            raise TypeError("Cannot construct a '{}' from "
                            "'{}'".format(cls, string))


class MACArray(NumPyBackedExtensionArrayMixin):
    """Array for MAC Address data.

    * https://en.wikipedia.org/wiki/MAC_address
    * https://tools.ietf.org/html/rfc5342
    """
    # What type(s) do we support?
    # MAC-48 or EUI-64?
    _dtype = MACType()
    _itemsize = 8
    ndim = 1
    can_hold_na = True

    def __init__(self, values, copy=True):
        # TODO: parse hex / strings
        self.data = np.array(values, dtype='uint64', copy=copy)

    @classmethod
    def _from_ndarray(cls, data, copy=False):
        return cls(data, copy=copy)

    @property
    def na_value(self):
        return self.dtype.na_value

    def __repr__(self):
        formatted = self._format_values()
        return "MACArray({!r})".format(formatted)

    def _format_values(self):
        return [_format(x) for x in self.data]

    @staticmethod
    def _box_scalar(scalar):
        return scalar

    def __setitem__(self, key, value):
        value = to_macaddress(value)
        self.data[key] = value

    def __iter__(self):
        return iter(self.data.tolist())

    def __lt__(self, other):
        return self.data < other

    def __le__(self, other):
        return self.data <= other

    def __eq__(self, other):
        return self.data == other

    def __ge__(self, other):
        return other <= self

    def __gt__(self, other):
        return other < self

    def equals(self, other):
        if not isinstance(other, type(self)):
            raise TypeError
        return (self.data == other.data).all()

    def _values_for_factorize(self):
        # Should hit pandas' UInt64Hashtable
        return self, 0

    def isna(self):
        return (self.data == 0)

    @property
    def _parser(self):
        return lambda x: x

    def take(self, indexer, allow_fill=True, fill_value=None):
        mask = indexer == -1
        result = self.data.take(indexer)
        result[mask] = self.dtype.na_value
        return type(self)(result, copy=False)

    def _formatting_values(self):
        return np.array(self._format_values(), dtype='object')

    @classmethod
    def _concat_same_type(cls, to_concat):
        return cls(np.concatenate([array.data for array in to_concat]))

    def take_nd(self, indexer, allow_fill=True, fill_value=None):
        return self.take(indexer, allow_fill=allow_fill, fill_value=fill_value)

    def copy(self, deep=False):
        return type(self)(self.data.copy())


def _format(mac):
    # https://stackoverflow.com/a/36883363/1889400
    mac_hex = "{:012x}".format(mac)
    mac_str = ":".join(mac_hex[i:i+2] for i in range(0, len(mac_hex), 2))
    return mac_str


def _parse(mac):
    # https://stackoverflow.com/a/36883363/1889400
    mac_int = int(mac.replace(":", "").replace("-", ""), 16)
    return mac_int


def to_macaddress(addresses):
    if (isinstance(addresses, six.string_types) or
            not isinstance(addresses, Iterable)):
        addresses = [addresses]

    addresses = [_parse(mac) if isinstance(mac, six.string_types) else mac
                 for mac in addresses]
    return np.array(addresses, dtype='u8')
