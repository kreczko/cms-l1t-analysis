import awkward
import pytest
import numpy as np
from rootpy.plotting import Hist

from cmsl1t.collections import VectorizedHistCollection
from cmsl1t.collections.vectorized import VectorizedBinProxy, VectorizedHistProxy


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
    collection.add('test', bins=[35, 90, 120])
    assert len(collection) == len(collection._innerBins) - 1


def test_access(collection):
    collection.add('test', bins=[35, 90, 120])
    innerValues = [1, 12, 1, 50]
    assert collection[innerValues] == collection[1] + collection[12] + collection[1] + collection[50]
    # assert type(collection[innerValues]) == Hist
    assert type(collection[innerValues]['test']) == VectorizedHistProxy


def test_copy(collection):
    proxy = VectorizedBinProxy(collection, [1, 12, 1, 50])


@pytest.mark.parametrize(
    "values,expected",
    [
        ([1, 12, 1, 50], [1, 12, 50]),
        ([1, 30, 12, 1, 50], [1, 12, 30, 50]),
    ])
def test_bin_proxy_flatten(collection, values, expected):
    proxy = VectorizedBinProxy(collection, values)
    assert proxy.flatten()._inner_indices.tolist() == expected

# def test_fill(collection):
#     innerValues = [1, 12, 1, 50]
#     outerValues = awkward.fromiter([
#         [60, 50, 40, 30, 20],
#         [32, 23],
#         [56, 34, 31],
#     ])
#     collection.add('test', bins=[35, 90, 120])
#     weights = np.ones(len(outerValues.content))
#     collection[innerValues][hist_name].fill(outerValues, weights)
