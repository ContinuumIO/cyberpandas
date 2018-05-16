# Cyberpandas

[![Build Status](https://travis-ci.org/ContinuumIO/cyberpandas.svg?branch=master)](https://travis-ci.org/ContinuumIO/cyberpandas)
[![Documentation Status](https://readthedocs.org/projects/cyberpandas/badge/?version=latest)](http://cyberpandas.readthedocs.io/en/latest/?badge=latest)

Cyberpandas provides support for storing IP and MAC address data inside a pandas DataFrame using pandas' [Extension Array Interface](http://pandas-docs.github.io/pandas-docs-travis/extending.html#extension-types)

```python
In [1]: from cyberpandas import IPArray

In [2]: import pandas as pd

In [3]: df = pd.DataFrame({"address": IPArray(['192.168.1.1', '192.168.1.10'])})

In [4]: df
Out[4]:
        address
0   192.168.1.1
1  192.168.1.10
```

See the [documentation](https://cyberpandas.readthedocs.io/en/latest/) for more.

## Installation

With Conda:

    conda install -c conda-forge cyberpandas

Or from PyPI

    pip install cyberpandas


