import ipaddress
import struct
import typing as T

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
    from .block import IPAddress

    if not is_list_like(values):
        values = [values]

    return IPAddress(_to_int_pairs(values))


def _to_int_pairs(values):
    if isinstance(values, (str, bytes, int)):
        values = ipaddress.ip_address(values)._ip
        return unpack(pack(values))
    else:
        values = [ipaddress.ip_address(v)._ip for v in values]
        values = [unpack(pack(v)) for v in values]
    return values


def _to_ipaddress_pyint(values):
    from .block import IPAddress

    values2 = (unpack(pack(x)) for x in values)
    return IPAddress(list(values2))


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
