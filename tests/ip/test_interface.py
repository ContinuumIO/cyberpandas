import pytest
from pandas.tests.extension import base

import cyberpandas as ip


@pytest.fixture
def dtype():
    return ip.IPType()


@pytest.fixture
def data():
    return ip.IPArray(list(range(100)))


@pytest.fixture
def data_missing():
    return ip.IPArray([0, 1])


@pytest.fixture(params=['data', 'data_missing'])
def all_data(request, data, data_missing):
    """Parametrized fixture giving 'data' and 'data_missing'"""
    if request.param == 'data':
        return data
    elif request.param == 'data_missing':
        return data_missing


@pytest.fixture
def data_for_sorting():
    return ip.IPArray([10, 2 ** 64 + 1, 1])


@pytest.fixture
def data_missing_for_sorting():
    return ip.IPArray([2 ** 64 + 1, 0, 1])


@pytest.fixture
def data_for_grouping():
    b = 1
    a = 2 ** 32 + 1
    c = 2 ** 32 + 10
    return ip.IPArray([
        b, b, 0, 0, a, a, b, c
    ])


@pytest.fixture
def data_repeated(data):
    def gen(count):
        for _ in range(count):
            yield data
    return gen


@pytest.fixture
def na_cmp():
    """Binary operator for comparing NA values.

    Should return a function of two arguments that returns
    True if both arguments are (scalar) NA for your type.

    By defult, uses ``operator.or``
    """
    return lambda x, y: int(x) == int(y) == 0


@pytest.fixture
def na_value():
    return ip.IPType.na_value


class TestDtype(base.BaseDtypeTests):
    pass


class TestInterface(base.BaseInterfaceTests):
    pass


class TestConstructors(base.BaseConstructorsTests):
    pass


class TestReshaping(base.BaseReshapingTests):
    @pytest.mark.skip("We consider 0 to be NA.")
    def test_stack(self):
        pass

    @pytest.mark.skip("We consider 0 to be NA.")
    def test_unstack(self):
        pass


class TestGetitem(base.BaseGetitemTests):
    pass


class TestMissing(base.BaseMissingTests):
    pass


class TestMethods(base.BaseMethodsTests):
    @pytest.mark.parametrize('dropna', [True, False])
    @pytest.mark.xfail(reason='upstream')
    def test_value_counts(data, dropna):
        pass

    @pytest.mark.skip(reason='0 for NA')
    def test_combine_le(self, data_repeated):
        super().test_combine_le(data_repeated)

    @pytest.mark.skip(reason='No __add__')
    def test_combine_add(self, data_repeated):
        super().test_combine_add(data_repeated)

    @pytest.mark.xfail(reason="buggy comparison of v4 and v6")
    def test_searchsorted(self, data_for_sorting, as_series):
        return super().test_searchsorted(data_for_sorting, as_series)


