.. _usage:

Usage
=====

This document describes how to use the methods and classes provided by
``cyberpandas``.

We'll assume that the following imports have been performed.

.. ipython:: python

   import ipaddress
   import pandas as pd
   from cyberpandas import IPArray, to_ipaddress

Parsing
-------

First, you'll need some IP Address data. Much like pandas'
:func:`pandas.to_datetime`, ``cyberpandas`` provides :func:`to_ipaddress` for
converting sequences of anything to a specialized array, :class:`IPArray` in
this case.

From Strings
""""""""""""

:func:`to_ipaddress` can parse a sequence strings where each element represents
an IP address.

.. ipython:: python

   to_ipaddress([
       '192.168.1.1',
       '2001:0db8:85a3:0000:0000:8a2e:0370:7334',
   ])

You can also parse a *container* of bytes (Python 2 parlance).

.. ipython:: python

   to_ipaddress([
       b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xc0\xa8\x01\x01',
       b' \x01\r\xb8\x85\xa3\x00\x00\x00\x00\x8a.\x03ps4',
   ])

If you have a buffer / bytestring, see :ref:`from_bytes`.

From Integers
"""""""""""""

IP Addresses are just integers, and :func:`to_ipaddress` can parse a sequence of
them.

.. ipython:: python

   to_ipaddress([
      3232235777,
      42540766452641154071740215577757643572
   ])

There's also the :meth:`IPArray.from_pyints` method that does the same thing.

.. _from_bytes:

From Bytes
""""""""""

If you have a correctly structured buffer of bytes or bytestring, you can
directly construct an ``IPArray`` without any intermediate copies.

.. ipython:: python

   stream = (b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xc0\xa8\x01'
             b'\x01 \x01\r\xb8\x85\xa3\x00\x00\x00\x00\x8a.\x03ps4')
   IPArray.from_bytes(stream)

``stream`` is expected to be a sequence of bytes representing IP Addresses (note
that it's just a bytestring that's be split across two lines for readability).
Each IP Address should be 128 bits, left padded with 0s for IPv4 addresses.
In particular, :meth:`IPArray.to_bytes` produces such a sequence of bytes.

Pandas Integration
------------------

``IPArray`` satisfies pandas extension array interface, which means that it can
safely be stored inside pandas' Series and DataFrame.

.. ipython:: python

   values = to_ipaddress([
       0,
       3232235777,
       42540766452641154071740215577757643572
   ])
   values      

   ser = pd.Series(values)
   ser
   df = pd.DataFrame({"addresses": values})
   df

Most pandas methods that make sense should work. The following section will call
out points of interest.

Indexing
""""""""

If your selection returns a scalar, you get back an
:class:`ipaddress.IPv4Address` or :class:`ipaddress.IPv6Address`.

.. ipython:: python

   ser[0]
   df.loc[2, 'addresses']

Missing Data
""""""""""""

The address 0 (``0.0.0.0``) is used to represent missing values.

.. ipython:: python

   ser.isna()
   ser.dropna()

IP Accessor
-----------

``cyberpandas`` offers an accessor for IP-specific methods.

.. ipython:: python

   ser.ip.isna
   df['addresses'].ip.is_ipv6
