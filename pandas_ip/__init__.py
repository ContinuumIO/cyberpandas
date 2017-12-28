"""Custom IP address dtype / block for pandas"""

from .block import IPBlock, IPType, IPAddress, IPAccessor, IPAddressIndex  # noqa
from .parser import to_ipaddress  # noqa

from pkg_resources import get_distribution, DistributionNotFound
try:
    __version__ = get_distribution(__name__).version
except DistributionNotFound:
    # package is not installed
    pass
