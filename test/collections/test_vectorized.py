import pytest
import numpy as np
from rootpy.plotting import Hist

from cmsl1t.collections import VectorizedHistCollection


@pytest.mark.parametrize(
    "values,expected",
    [
        ([1, 12, 1, 50], [1, 2, 1, 5]),
        ([1, 11, 1111], [1, 2, 6]),
        ([-10, 1111, 20], [0, 6, 4]),
    ])
def test_inner_index(values, expected):
    innerBins = np.array([0, 10, 15, 20, 30, 999])
    coll = VectorizedHistCollection(innerBins)

    np.testing.assert_array_equal(coll._get_inner_indices(values), expected)
