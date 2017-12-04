import ipaddress

import numpy as np
from pandas.core.internals import NonConsolidatableMixIn, Block


class IPBlock(NonConsolidatableMixIn, Block):
    """Block type for IP Address dtype

    Notes
    -----
    This can hold either IPv4 or IPv6 addresses.

    """

    _holder = np.ndarray

    def formatting_values(self):
        return [self._cls._string_from_ip_int(x) for x in self.values.tolist()]

    def concat_same_type(self, to_concat, placement=None):
        pass


if __name__ == '__main__':
    ip4 = IPBlock(np.array([10, 12], dtype=np.uint16), slice(0, 3))
    ip6 = IPBlock(np.array([10, 12], dtype=np.uint16), slice(0, 3), version=6)
