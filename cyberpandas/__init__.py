"""Custom IP address dtype / block for pandas"""

from .ip_array import (
    IPType,
    IPArray,
    IPAccessor,
)
from .ip_methods import ip_range
from .parser import to_ipaddress
from .mac_array import MACType, MACArray

from pkg_resources import get_distribution, DistributionNotFound
try:
    __version__ = get_distribution(__name__).version
except DistributionNotFound:
    # package is not installed
    pass

del get_distribution
del DistributionNotFound


__all__ = [
    '__version__',
    'IPAccessor',
    'IPArray',
    'IPType',
    'MACArray',
    'MACType',
    'ip_range',
    'to_ipaddress',
]
