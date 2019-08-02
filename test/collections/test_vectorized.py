import awkward
import pytest
import numpy as np

from cmsl1t.collections import VectorizedHistCollection
from cmsl1t.collections.vectorized import VectorizedBinProxy, VectorizedHistProxy, extend, split_input


@pytest.fixture
def collection():
    innerBins = np.array([0, 10, 15, 20, 30, 999])
    coll = VectorizedHistCollection(innerBins)
    # fill for [35, 90, 120]
    return coll


@pytest.mark.parametrize(
    "values,expected",
    [
        ([1, 12, 1, 50], [1, 2, 1, 5]),
        ([1, 11, 1111], [1, 2, 6]),
        ([-10, 1111, 20], [0, 6, 4]),
    ])
def test_inner_index(collection, values, expected):
    np.testing.assert_array_equal(collection._get_inner_indices(values), expected)


def test_add(collection):
    assert len(collection) == 0
    collection.insert('test', bins=[35, 90, 120])
    assert len(collection) == len(collection._innerBins) - 1


def test_access(collection):
    collection.insert('test', bins=[35, 90, 120])
    innerValues = [1, 12, 1, 50]
    assert collection[innerValues] == collection[1] + collection[12] + collection[1] + collection[50]
    # assert type(collection[innerValues]) == Hist
    assert type(collection[innerValues]['test']) == VectorizedHistProxy


# def test_copy(collection):
#     proxy = VectorizedBinProxy(collection, [1, 12, 1, 50])


@pytest.mark.parametrize(
    "values,expected",
    [
        ([1, 12, 1, 50], [1, 12, 50]),
        ([1, 30, 12, 1, 50], [1, 12, 30, 50]),
    ])
def test_bin_proxy_flatten(collection, values, expected):
    proxy = VectorizedBinProxy(collection, values)
    assert proxy.flatten()._inner_indices.tolist() == expected


@pytest.mark.parametrize(
    "bins, x, expected",
    [
        (
            np.array([1, 12, 1, 50]),
            np.array([10, 20, 30, 40]),
            [np.array([10, 30]), np.array([20]), np.array([40])]
        ),
        (
            np.array([1, 1, 1, 2, 1, 2]),
            np.array([10, 20, 30, 40, 50, 60]),
            [np.array([10, 20, 30, 50]), np.array([40, 60])]
        ),
    ])
def test_split(bins, x, expected):
    unique_bins = np.unique(bins)
    result = []
    for b in unique_bins:
        result.append(x[bins == b])
    for chunk, exp in zip(result, expected):
        assert chunk.tolist() == exp.tolist()


def test_fill(collection):
    innerValues = [1, 12, 1, 50]
    outerValues = awkward.fromiter([
        [60, 50, 40, 30, 20],
        [32, 23],
        [56, 34, 31],
        [],
    ])
    expected = [
        [4.0, 4.0, 0.0, 0.0],
        [2.0, 0.0, 0.0, 0.0],
        [0.0, 0.0, 0.0, 0.0],
    ]

    hist_name = 'test'
    collection.insert(hist_name, bins=[35, 90, 120])
    weights = np.ones(len(outerValues.content))
    collection[innerValues][hist_name].fill(outerValues, weights)
    for i in range(len(np.unique(innerValues))):
        hist = collection[innerValues][hist_name]._get_hist(i + 1)
        assert list(hist.y(overflow=True)) == expected[i]


def test_extend():
    innerValues = [1, 12, 1, 50]
    outerValues = awkward.fromiter([
        [60, 50, 40, 30, 20],
        [32, 23],
        [56, 34, 31],
        [],
    ])
    innerValues = extend(innerValues, outerValues.starts, outerValues.stops)
    assert len(innerValues) == len(outerValues.content)


def test_split_input():
    innerValues = [1, 12, 1, 50]
    outerValues = awkward.fromiter([
        [60, 50, 40, 30, 20],
        [32, 23],
        [56, 34, 31],
        [],
    ])
    weights = np.ones(len(outerValues.content))

    expected = [
        (1, [60, 50, 40, 30, 20, 56, 34, 31], list(np.ones(8))),
        [12, [32, 23], list(np.ones(2))],
    ]
    results = list(split_input(innerValues, outerValues, weights))
    assert len(results) == len(expected)
    for r, e in zip(results, expected):
        i, o, w = r
        i_e, o_e, w_e = e
        assert i == i_e
        assert o.tolist() == o_e
        assert w.tolist() == w_e
