"""Utilities for working with IP address data."""
import struct

import six


def to_bytes(n, length, byteorder='big'):
    # https://stackoverflow.com/a/20793663/1889400
    h = '%x' % n
    s = ('0' * (len(h) % 2) + h).zfill(length * 2).decode('hex')
    return s if byteorder == 'big' else s[::-1]


def pack(ip):
    # type: (int) -> bytes
    if six.PY2:
        return to_bytes(ip, length=16, byteorder='big')
    else:
        return ip.to_bytes(16, byteorder='big')


def unpack(ip):
    # type: (T.Tuple[int, int]) -> int, int
    # Recipe 3.5 from Python Cookbook 3rd ed. (p. 90)
    # int.from_bytes(data, 'big') for Py3+
    hi, lo = struct.unpack(">QQ", ip)
    return hi, lo


def combine(hi, lo):
    # type: (int, int) -> int
    """Combine the hi and lo bytes into the final ip address."""
    return (hi << 64) + lo
