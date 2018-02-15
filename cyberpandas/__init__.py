"""Custom IP address dtype / block for pandas"""

from .ip_array import (  # noqa
    IPType,
    IPArray,
    IPAccessor,
    IPAddressIndex,
)
from .parser import to_ipaddress  # noqa

from pkg_resources import get_distribution, DistributionNotFound
try:
    __version__ = get_distribution(__name__).version
except DistributionNotFound:
    # package is not installed
    pass
