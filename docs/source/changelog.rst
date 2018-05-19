#########
Changelog
#########

*************
Version 1.1.0
*************

- Added :func:`ip_range` for generating an array of regularly-spaced IP addresses (:issue:`27`).
- Added :meth:`IPArray.netmask` and :meth:`IPArray.hostmask` (:issue:`30`).
- Fixed Python 2 dependencies so that the `ipaddress` backport is installed automatically when install cyberpandas from PyPI (:issue:`29`).
