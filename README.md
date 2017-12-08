# pandas-ip

IP Address dtype and block for pandas

# PEP

Abstract
==========

Proposal to add support for storing and operating on IP Address data. Adds a new
block type for ip address data and an `ip` accessor to `Series` and `Index`.


Rationale
============

For some communities, IP and MAC addresses are a common data format. Python 3.3
added the `ipaddress` module to the standard library.


Alternatives
===============

1. Store `ipaddress.IPv4Address` or `ipaddress.IPv6Address` objects in an
   `object` dtype array. Not performent.
2. A separate library that provides a container and methods. More friction
   when using dataframes for other data.
