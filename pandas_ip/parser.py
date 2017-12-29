import ipaddress
import struct
import typing as T

import numpy as np
from pandas.api.types import is_list_like


def to_ipaddress(values):
    """Convert values to IPAddress

    Parameters
    ----------
    values : int, str, bytes, or sequence of those

    Returns
    -------
    addresses : IPAddress

    Examples
    --------
    Parse strings
    >>> to_ipaddress(['192.168.1.1',
    ...               '2001:0db8:85a3:0000:0000:8a2e:0370:7334'])
    <IPAddress(['192.168.1.1', '0:8a2e:370:7334:2001:db8:85a3:0'])>

    Or integers
    >>> to_ipaddress([3232235777,
                      42540766452641154071740215577757643572])
    <IPAddress(['192.168.1.1', '0:8a2e:370:7334:2001:db8:85a3:0'])>

    Or packed binary representations
    >>> to_ipaddress([b'\xc0\xa8\x01\x01',
                      b' \x01\r\xb8\x85\xa3\x00\x00\x00\x00\x8a.\x03ps4'])
    <IPAddress(['192.168.1.1', '0:8a2e:370:7334:2001:db8:85a3:0'])>
    """
    from . import IPAddress

    if not is_list_like(values):
        values = [values]

    return IPAddress(_to_ip_array(values))


def _to_ip_array(values):
    from .block import IPType

    if not (isinstance(values, np.ndarray) and values.dtype == IPType.base):
        values = _to_int_pairs(values)
    return np.atleast_1d(np.asarray(values, dtype=IPType.base))


def _to_int_pairs(values):
    if isinstance(values, (str, bytes, int)):
        values = ipaddress.ip_address(values)._ip
        return unpack(pack(values))
    elif isinstance(values, np.ndarray):
        if values.ndim != 2:
            raise ValueError("'values' should be a 2-D when passing a "
                             "NumPy array.")
        if values.dtype != int:
            raise ValueError("'values' should be integer dtype when "
                             "passing a NumPy array.")
    elif isinstance(values, tuple) and len(values) == 2:
        # like IPAddress((0, 0))
        # which isn't IPAddress([0, 0])
        pass
    elif all(isinstance(x, tuple) for x in values):
        # TODO: not great
        pass
    else:
        values = [ipaddress.ip_address(v)._ip for v in values]
        values = [unpack(pack(v)) for v in values]
    return values


def _to_ipaddress_pyint(values):
    from .block import IPType

    values2 = [unpack(pack(x)) for x in values]
    return np.atleast_1d(np.asarray(values2, dtype=IPType.base))


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
