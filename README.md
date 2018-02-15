Discussion at https://github.com/pandas-dev/pandas/issues/18767

## Install

This requires some modifications to pandas. These modifications are being
merged upstream in pandas, but for now you can install from my channel with

```
conda install -c TomAugspurger pandas cyberpandas
```

## Abstract

Proposal to add support for storing and operating on IP Address data.
Adds a new block type for ip address data and an `ip` accessor to
`Series` and `Index`.

## Rationale

For some communities, IP and MAC addresses are a common data format. The data
format was deemed important enough to add the `ipaddress` module to the standard
library (see `PEP 3144`_). At Anaconda, we hear from customers who would use a
first-class IP address array container if it existed in pandas.

I turned to StackOverflow to gauge interest in this topic. A search for "IP" on
the [pandas stackoverflow
tag](https://stackoverflow.com/search?q=%5Bpandas%5D+IP) turns up 300 results.
Under the NumPy tag there are another 80. For comparison, I ran a few other
searches to see what interest there is in other "specialized" data types (this
is a very rough, probably incorrect, way of estimating interest):

| term      | results |
| --------- | ------- |
| financial | 251     |
| geo       | 120     |
| ip        | 300     |
| logs      | 590     |


Categorical, which is already in pandas, turned up 1,089 items.

Overall, I think there's enough interest relative to the implementation /
maintenance burden to warrant adding the support for IP Addresses. I don't
anticipate this causing any issues for the arrow transition, once ARROW-1587 is
in place. We can be careful which parts of the storage layer are implementation
details.

## Specification

The proposal is to add

1.  A type and container for IPArray and MACAddress (similar to
    `CategoricalDtype` and `Categorical`).
2.  A block for IPArray and MACAddress (similar to `CategoricalBlock`).
3.  A new accessor for Series and Indexes, `.ip`, for operating on IP
    addresses and MAC addresses (similar to `.cat`).

The type and block should be generic IP address blocks, with no
distinction between IPv4 and IPv6 addresses. In our experience, it's
common to work with data from multiple sources, some of which may be
IPv4, and some of which may be IPv6. This also matches the semantics
of the default `ipaddress.ip_address` factory function, which returns
an `IPv4Address` or `IPv6Address` as needed. Being able to deal with
ip addresses in an IPv4 vs. IPv6 agnostic fashion is useful.

### Data Layout

Since IPv6 addresses are 128 bits, they do not fit into a standard NumPy uint64
space. This complicates the implementation (but, gives weight to accepting the
proposal, since doing this on your own can be tricky).

Each record will be composed of two uint64s. The first element 
contains the first 64 bits, and the second array contains the second 64
bits. As a NumPy structured dtype, that's

```python
base = np.dtype([('lo', '>u8'), ('hi', '>u8')])
```

This is a common format for handling IPv4 and IPv6 data:

> Hybrid dual-stack IPv6/IPv4 implementations recognize a special class of
> addresses, the IPv4-mapped IPv6 addresses. These addresses consist of an
> 80-bit prefix of zeros, the next 16 bits are one, and the remaining,
> least-significant 32 bits contain the IPv4 address.

From [here](https://en.wikipedia.org/wiki/IPv6#Software)

### Missing Data

Use the lowest possible IP address as a marker. According to RFC2373,

> The address 0:0:0:0:0:0:0:0 is called the unspecified address. It must
> never be assigned to any node. It indicates the absence of an address.

See [here](https://tools.ietf.org/html/rfc2373.html#section-2.5.2).

### Methods

The new user-facing `IPArray` (analogous to a `Categorical`) will have
a few methods for easily constructing arrays of IP addresses.

```python
IPArray.from_pyints(cls, values: Sequence[int]) -> 'IPArray':
    """Construct an IPArray array from a sequence of python integers.

    >>> IPArray.from_pyints([10, 18446744073709551616])
    <IPArray(['0.0.0.10', '::1'])>
    """

IPArray.from_str(cls, values: Sequence[str]) -> 'IPArray':
    """Construct an IPArray from a sequence of strings."""
```

The methods in the new `.ip` namespace should follow the standard
library's design.

**Properties**

-   `is_multicast`
-   `is_private`
-   `is_global`
-   `is_unspecificed`
-   `is_reserved`
-   `is_loopback`
-   `is_link_local`

### Reference Implementation

An implementation of the types and block is available at
[cyberpandas](https://github.com/ContinuumIO/cyberpandas/) (at the moment
it's a proof of concept).

### Alternatives

Adding a new block type to pandas is a major change. Downstream libraries may
have special-cased handling for pandas' extension types, so this shouldn't be
adopted without careful consideration.

Some alternatives to this that exist outside of pandas:

1.  Store `ipaddress.IPv4Address` or `ipaddress.IPv6Address` objects in
    an `object` dtype array. The `.ip` namespace could still be included
    with an extension decorator. The drawback here is the poor
    performance, as every operation would be done element-wise.
2.  A separate library that provides a container and methods. The
    downside here is that the library would need to subclass `Series`,
    `DataFrame`, and `Index` so that the custom blocks and types are
    interpreted correctly. Users would need to use the custom
    `IPSeries`, `IPDataFrame`, etc., which increases friction when working
    with other libraries that may expect / coerce to pandas objects.

To expand a bit on the (current) downside of alternative 2,  when the pandas constructors
see an "unknown" object, they falls back to `object` dtype and stuffs the actual Python object
into whatever container is being created:

```python
In [1]: import pandas as pd

In [2]: import cyberpandas as ip

In [3]: arr = ip.IPArray.from_pyints([1, 2])

In [4]: arr
Out[4]: <IPArray(['0.0.0.1', '0.0.0.2'])>

In [5]: pd.Series(arr)
Out[5]:
0    <IPArray(['0.0.0.1', '0.0.0.2'])>
dtype: object
```

I'd rather not have to make a subclass of Series, just to stick an array-like thing into a Series.

If pandas could provide an interface such that objects satisfying that interface
are treated as array-like, and not a simple python object, then I'll gladly close
this issue and develop the IP-address specific functionality in another package.
That might be the best possible outcome to all this.

### References

-   [cyberpandas](https://github.com/ContinuumIO/cyberpandas/)
-   [PEP 3144](https://www.python.org/dev/peps/pep-3144/)
-   [RFC 2373](https://tools.ietf.org/html/rfc2373.html#section-2.5.2)
-   [ipaddress howto](https://docs.python.org/3/howto/ipaddress.html)
-   [ipaddress](https://docs.python.org/3/library/ipaddress.html)
