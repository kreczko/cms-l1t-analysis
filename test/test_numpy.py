import numba
import numpy as np
import pytest

from cmsl1t.math import isin_nd

group_1 = np.array([(1, 2), (3, 3), (5, 7), (4, 4)])
group_2 = np.array([(0, 0), (1, 2), (2, 2), (3, 3)])
test_elements = np.array([(1, 2), (3, 3), (3, 5)])


@numba.jit(nopython=True, parallel=True)
def filter_lumis(ranges_to_test, valid_lumi_sections):
    result = np.zeros(ranges_to_test.shape[0], dtype=np.uint8)
    for i in range(valid_lumi_sections.shape[0]):
        valid_section = valid_lumi_sections[i, :]
        for j in range(ranges_to_test.shape[0]):
            to_test = ranges_to_test[j, :]
            if np.equal(to_test, valid_section).all():
                result[j] = 1
    return result


def pyhep_solution(ranges_to_test, valid_lumi_sections):
    """
        From https://github.com/JelleAalbers
    """
    test_elements_expanded = np.expand_dims(ranges_to_test, axis=1)
    entries_equal = test_elements_expanded == valid_lumi_sections
    tuple_equal = np.all(entries_equal, axis=2)
    return np.any(tuple_equal, axis=1)


@pytest.mark.parametrize(
    "group, expected",
    [
        (group_1, [True, True, False]),
        (group_2, [True, True, False]),
    ])
def test_numba(group, expected):
    mask = filter_lumis(test_elements, group)
    assert mask.tolist() == expected


@pytest.mark.parametrize(
    "group, expected",
    [
        (group_1, [True, True, False]),
        (group_2, [True, True, False]),
    ])
def test_pyhep(group, expected):
    mask = pyhep_solution(test_elements, group)
    assert mask.tolist() == expected


@pytest.mark.parametrize(
    "group, expected",
    [
        (group_1, [True, True, False]),
        (group_2, [True, True, False]),
    ])
def test_stackoverflow(group, expected):
    mask = isin_nd(test_elements, group)
    assert mask.tolist() == expected
