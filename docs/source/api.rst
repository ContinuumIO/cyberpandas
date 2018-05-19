API
===

.. currentmodule:: cyberpandas

Cyberpandas provides two extension types, :class:`IPArray` and :class:`MACArray`.

:class:`IP Array`
-----------------

.. autoclass:: IPArray

Constructors
""""""""""""

The class constructor is flexible, and accepts integers, strings, or bytes.
Dedicated alternate constructors are also available.

.. automethod:: IPArray.from_pyints
.. automethod:: IPArray.from_bytes

Finally, the top-level ``ip_range`` method can be used.

.. automethod:: ip_range

Serialization
"""""""""""""

Convert the IPArray to various formats.

.. automethod:: IPArray.to_pyipaddress
.. automethod:: IPArray.to_pyints
.. automethod:: IPArray.to_bytes


Methods
"""""""

Various methods that are useful for pandas. When a Series contains
an IPArray, calling the Series method will dispatch to these methods.

.. automethod:: IPArray.take
.. automethod:: IPArray.unique
.. automethod:: IPArray.isin
.. automethod:: IPArray.isna
.. autoattribute:: IPArray.netmask

IP Address Attributes
"""""""""""""""""""""

IP addresss-specific attributes.

.. autoattribute:: IPArray.is_ipv4
.. autoattribute:: IPArray.is_ipv6
.. autoattribute:: IPArray.version
.. autoattribute:: IPArray.is_multicast
.. autoattribute:: IPArray.is_private
.. autoattribute:: IPArray.is_global
.. autoattribute:: IPArray.is_unspecified
.. autoattribute:: IPArray.is_reserved
.. autoattribute:: IPArray.is_loopback
.. autoattribute:: IPArray.is_link_local
.. automethod:: IPArray.netmask
.. automethod:: IPArray.hostmask



:class:`MACArray`
-----------------

.. autoclass:: MACArray
