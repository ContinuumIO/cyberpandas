import ipaddress

import struct
import typing as T
from typing import Tuple

_IPv4_MAX = 2 ** 32 - 1
_IPv6_MAX = 2 ** 128 - 1
_U8_MAX = 2 ** 64 - 1


def _to_int_pairs(values):
    if isinstance(values, (str, bytes, int)):
        values = ipaddress.ip_address(values)._ip
        return unpack(pack(values))
    else:
        values = [ipaddress.ip_address(v)._ip for v in values]
        values = [unpack(pack(v)) for v in values]
    return values


def is_ipv4(value) -> bool:
    if isinstance(value, str):
        return value.count(".") == 3
    elif isinstance(value, bytes):
        pass
    elif isinstance(value, int):
        return value < _IPv4_MAX
    else:
        return False


def is_ipv6(value) -> bool:
    if isinstance(value, str):
        return value.count(":") == 7


# Item parsers

def _parse_ipv4_str(value: str) -> Tuple[int, int]:
    pass


def _parse_ipv6_str(value: str) -> Tuple[int, int]:
    pass


# Array parsers

def _to_ipaddress_str(value):
    pass


def to_ipaddress(values: T.Iterable):
    """Parse an array of things into an IPAddress"""
    if isinstance(str):
        return _to_ipaddress_str(values)


def _to_ipaddress_pyint(values):
    from .block import IPAddress

    values2 = (unpack(pack(x)) for x in values)
    return IPAddress(list(values2))


def _to_ipaddress_bytes(values):
    pass


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
