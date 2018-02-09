from .common import _IPv4_MAX


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
