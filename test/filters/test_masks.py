import numpy as np
import pytest

from cmsl1t.filters import combine_with_AND, combine_with_OR


scalar_filters_all_passing = [True, True, True]
scalar_filters_all_failing = [False, False, False]
scalar_filters_all_but_one_failing = [False, True, False]
vector_filters_all_passing = [
    np.array([True, True, True]),
    np.array([True, True, True]),
    np.array([True, True, True]),
    np.array([True, True, True]),
]
vector_filters_all_failing = [
    np.array([False, False, False]),
    np.array([False, False, False]),
    np.array([False, False, False]),
    np.array([False, False, False]),
]

vector_filters_all_but_one_failing = [
    np.array([False, False, False]),
    np.array([False, True, False]),
    np.array([False, False, False]),
    np.array([False, False, False]),
]


@pytest.mark.parametrize('filters, expected', [
    (scalar_filters_all_passing, True),
    (scalar_filters_all_failing, False),
    (scalar_filters_all_but_one_failing, False),
    (vector_filters_all_passing, [True, True, True, True]),
    (vector_filters_all_failing, [False, False, False, False]),
    (vector_filters_all_but_one_failing, [False, False, False, False]),
]
)
def test_combine_with_AND(filters, expected):
    result = combine_with_AND(filters)
    assert np.size(result) == np.size(expected)
    assert result == expected


@pytest.mark.parametrize('filters, expected', [
    (scalar_filters_all_passing, True),
    (scalar_filters_all_failing, False),
    (scalar_filters_all_but_one_failing, True),
    (vector_filters_all_passing, [True, True, True, True]),
    (vector_filters_all_failing, [False, False, False, False]),
    (vector_filters_all_but_one_failing, [False, True, False, False]),
]
)
def test_combine_with_OR(filters, expected):
    result = combine_with_OR(filters)
    assert np.size(result) == np.size(expected)
    assert result == expected
