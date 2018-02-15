import ipaddress

import numpy as np
from pandas.api.types import is_list_like

from ._utils import pack, unpack


def to_ipaddress(values):
    """Convert values to IPArray

    Parameters
    ----------
    values : int, str, bytes, or sequence of those

    Returns
    -------
    addresses : IPArray

    Examples
    --------
    Parse strings
    >>> to_ipaddress(['192.168.1.1',
    ...               '2001:0db8:85a3:0000:0000:8a2e:0370:7334'])
    <IPArray(['192.168.1.1', '0:8a2e:370:7334:2001:db8:85a3:0'])>

    Or integers
    >>> to_ipaddress([3232235777,
                      42540766452641154071740215577757643572])
    <IPArray(['192.168.1.1', '0:8a2e:370:7334:2001:db8:85a3:0'])>

    Or packed binary representations
    >>> to_ipaddress([b'\xc0\xa8\x01\x01',
                      b' \x01\r\xb8\x85\xa3\x00\x00\x00\x00\x8a.\x03ps4'])
    <IPArray(['192.168.1.1', '0:8a2e:370:7334:2001:db8:85a3:0'])>
    """
    from . import IPArray

    if not is_list_like(values):
        values = [values]

    return IPArray(_to_ip_array(values))


def _to_ip_array(values):
    from .ip_array import IPType, IPArray

    if isinstance(values, IPArray):
        return values.data
    if not (isinstance(values, np.ndarray) and values.dtype == IPType.mybase):
        values = _to_int_pairs(values)
    return np.atleast_1d(np.asarray(values, dtype=IPType.mybase))


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
        # like IPArray((0, 0))
        # which isn't IPArray([0, 0])
        pass
    elif all(isinstance(x, tuple) for x in values):
        # TODO: not great
        pass
    else:
        values = [ipaddress.ip_address(v)._ip for v in values]
        values = [unpack(pack(v)) for v in values]
    return values


def _to_ipaddress_pyint(values):
    from .ip_array import IPType

    values2 = [unpack(pack(x)) for x in values]
    return np.atleast_1d(np.asarray(values2, dtype=IPType.mybase))
