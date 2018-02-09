import pytest
from pandas.tests.extension.base import BaseArrayTests

import cyberpandas as ip


class TestIP(BaseArrayTests):
    @pytest.fixture
    def data(self):
        return ip.IPAddress(list(range(100)))

    @pytest.fixture
    def data_missing(self):
        return ip.IPAddress([0, 1])

    @pytest.fixture
    def na_cmp(self):
        """Binary operator for comparing NA values.

        Should return a function of two arguments that returns
        True if both arguments are (scalar) NA for your type.

        By defult, uses ``operator.or``
        """
        return lambda x, y: int(x) == int(y) == 0
