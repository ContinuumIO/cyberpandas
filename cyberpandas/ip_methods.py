import ipaddress

import numpy as np
import six

from .ip_array import IPArray
from .common import _U8_MAX


def _as_int(ip):
    # type: (Union[int, str, IPv4Address, IPv6Address]) -> int
    if isinstance(ip, six.string_types):
        ip = ipaddress.ip_address(ip)
    return int(ip)


def _crosses_boundary(lo, hi):
    return (lo <= _U8_MAX) == (hi <= _U8_MAX)


def ip_range(start=None, stop=None, step=None):
    """Generate a range of IP Addresses

    Parameters
    ----------
    start : int, str, IPv4Address, or IPv6Address, optional
        Start of interval.  The interval includes this value.  The default
        start value is 0.
    start : int, str, IPv4Address, or IPv6Address, optional
        End of interval.  The interval does not include this value.
    step : int, optional
        Spacing between values.  For any output `out`, this is the distance
        between two adjacent values, ``out[i+1] - out[i]``.  The default
        step size is 1.  If `step` is specified as a position argument,
        `start` must also be given.

    Returns
    -------
    IPArray

    Notes
    -----
    Performance will worsen if either of `start` or `stop` are larger than
    2**64.

    Examples
    --------
    From integers

    >>> ip_range(1, 5)
    IPArray(['0.0.0.1', '0.0.0.2', '0.0.0.3', '0.0.0.4'])

    Or strings

    >>> ip_range('0.0.0.1', '0.0.0.5')
    IPArray(['0.0.0.1', '0.0.0.2', '0.0.0.3', '0.0.0.4'])

    Or `ipaddress` objects

    >>> ip_range(ipaddress.IPv4Address(1), ipaddress.IPv4Address(5))
    IPArray(['0.0.0.1', '0.0.0.2', '0.0.0.3', '0.0.0.4'])
    """
    if start is not None:
        start = _as_int(start)
    if stop is not None:
        stop = _as_int(stop)
    if step is not None:
        step = _as_int(step)
    arr = IPArray(np.arange(start, stop, step))
    return arr
