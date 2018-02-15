"""Utilities for working with IP address data."""
import struct


def pack(ip):
    # type: (int) -> bytes
    return ip.to_bytes(16, 'big')


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
