import operator

import numpy as np
import pandas as pd
import pandas.util.testing as tm
import pytest

import pandas_ip as ip


@pytest.fixture
def series():
    return pd.Series(ip.IPAddress.from_pyints([0, 1, 2]))


@pytest.fixture
def frame():
    return pd.DataFrame({"A": ip.IPAddress.from_pyints([0, 1, 2]),
                         "B": [0, 1, 2],
                         "C": ip.IPAddress.from_pyints([0, 1, 2])})


@pytest.fixture(params=['series', 'frame'])
def obj(request, series, frame):
    if request.param == 'series':
        return series
    elif request.param == 'frame':
        return frame


# -----
# Tests
# -----
@pytest.mark.parametrize('method', [
    operator.methodcaller('head'),
    operator.methodcaller('rename', str),
])
def test_works(obj, method):
    method(obj)


def test__take(frame):
    return frame._take([0], axis=0)


def test_iloc_series(series):
    series.iloc[slice(None)]
    series.iloc[0]
    series.iloc[[0]]
    series.iloc[[0, 1]]


def test_iloc_frame(frame):
    frame.iloc[:, 0]
    frame.iloc[:, [0]]
    frame.iloc[:, [0, 1]]
    frame.iloc[:, [0, 2]]

    frame.iloc[0, 0]
    frame.iloc[0, [0]]
    frame.iloc[0, [0, 1]]
    frame.iloc[0, [0, 2]]

    frame.iloc[[0], 0]
    frame.iloc[[0], [0]]
    frame.iloc[[0], [0, 1]]
    frame.iloc[[0], [0, 2]]


def test_loc_series(series):
    series.loc[:]
    series.loc[0]
    series.loc[1]
    series.loc[[0, 1]]


def test_loc_frame(frame):
    frame.loc[:, 'A']
    frame.loc[:, ['A']]
    frame.loc[:, ['A', 'B']]
    frame.loc[:, ['A', 'C']]

    frame.loc[0, 'A']
    frame.loc[0, ['A']]
    frame.loc[0, ['A', 'B']]
    frame.loc[0, ['A', 'C']]

    frame.loc[[0], 'A']
    frame.loc[[0], ['A']]
    frame.loc[[0], ['A', 'B']]
    frame.loc[[0], ['A', 'C']]


def test_reindex(frame):
    result = frame.reindex([0, 10])
    expected = pd.DataFrame({"A": ip.IPAddress.from_pyints([0, 0]),
                             "B": [0, np.nan],
                             "C": ip.IPAddress.from_pyints([0, 0])},
                            index=[0, 10])
    tm.assert_frame_equal(result, expected)
