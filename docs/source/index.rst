.. cyberpandas documentation master file, created by
   sphinx-quickstart on Wed Feb 21 10:27:45 2018.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

cyberpandas
===========

cyberpandas is a library for working with arrays of IP Addresses. It's
specifically designed to work well with pandas.

Install
=======

With conda

.. code-block:: none

   conda install -c conda-forge cyberpandas

Or pip

.. code-block:: none

   pip install cyberpandas

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

.. code-block:: python

   >>> from cyberpandas import IPArray
   >>> import pandas as pd

   >>> arr = IPArray([0, 1, 2])0000
   >>> arr

API
===

.. currentmodule:: cyberpandas


.. toctree::
   :maxdepth: 2
   :caption: Contents:



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
