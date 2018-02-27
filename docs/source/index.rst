.. cyberpandas documentation master file, created by
   sphinx-quickstart on Wed Feb 21 10:27:45 2018.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

cyberpandas
===========

cyberpandas is a library for working with arrays of IP Addresses. It's
specifically designed to work well with pandas.

Key Concepts
============

``IPType``
----------

This is a data type (like ``numpy.dtype('int64')`` or
``pandas.api.types.CategoricalDtype()``. For the most part, you won't interact
with ``IPType`` directly. It will be the value of the ``.dtype`` attribute on
your arrays.

``IPArray``
-----------

This is the container for your IPAddress data.

Usage
-----

.. ipython:: python

   from cyberpandas import IPArray
   import pandas as pd

   arr = IPArray(['192.168.1.1',
                  '2001:0db8:85a3:0000:0000:8a2e:0370:7334'])
   arr

``IPArray`` is a container for both IPv4 and IPv6 addresses. It can in turn be
stored in pandas' containers:

.. ipython:: python

   pd.Series(arr)
   pd.DataFrame({"addresses": arr})

See :ref:`usage` for more.

API
===

.. currentmodule:: cyberpandas


.. toctree::
   :maxdepth: 2
   :caption: Contents:

   install.rst
   usage.rst
   api.rst




Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
