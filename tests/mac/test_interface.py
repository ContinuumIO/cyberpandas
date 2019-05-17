import pytest

from pandas.tests.extension import base

from cyberpandas.mac_array import MACArray, MACType


@pytest.fixture
def dtype():
    return MACType()


@pytest.fixture
def data():
    return MACArray(list(range(100)))


@pytest.fixture
def data_missing():
    return MACArray([0, 1])


@pytest.fixture(params=['data', 'data_missing'])
def all_data(request, data, data_missing):
    """Parametrized fixture giving 'data' and 'data_missing'"""
    if request.param == 'data':
        return data
    elif request.param == 'data_missing':
        return data_missing


@pytest.fixture
def data_for_sorting():
    return MACArray([10, 2 ** 64 - 1, 1])


@pytest.fixture
def data_missing_for_sorting():
    return MACArray([2 ** 64 - 1, 0, 1])


@pytest.fixture
def data_for_grouping():
    b = 1
    a = 2 ** 32 + 1
    c = 2 ** 32 + 10
    return MACArray([
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
    return MACType.na_value


class TestDtype(base.BaseDtypeTests):
    pass


class TestInterface(base.BaseInterfaceTests):
    pass


class TestConstructors(base.BaseConstructorsTests):
    pass


class TestReshaping(base.BaseReshapingTests):
    @pytest.mark.skip(reason='Pandas inferrs us as int64.')
    def test_concat_mixed_dtypes(self):
        pass

    @pytest.mark.skip(reason="0 for null")
    def test_stack(self):
        pass

    @pytest.mark.skip(reason="0 for null")
    def test_unstack(self):
        pass


class TestGetitem(base.BaseGetitemTests):
    pass


class TestMissing(base.BaseMissingTests):
    pass


class TestMethods(base.BaseMethodsTests):
    @pytest.mark.xfail(reason='upstream')
    def test_value_counts(data, dropna):
        pass

    @pytest.mark.skip(reason="buggy comparison")
    def test_combine_le(self, data_repeated):
        super().test_combine_le(data_repeated)

    @pytest.mark.skip(reason="TODO")
    def test_hash_pandas_object_works(self):
        pass
