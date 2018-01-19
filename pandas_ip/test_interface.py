import pytest
from pandas.tests.extension_arrays.base import BaseArrayTests

import pandas_ip as ip


@pytest.fixture
def test_data():
    return ip.IPAddress(list(range(100)))


@pytest.fixture
def test_data_missing():
    return ip.IPAddress([0, 1])


class TestIP(BaseArrayTests):
    pass
