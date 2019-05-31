import numba
import numpy as np
import pytest

group_1 = np.array([(1, 2), (3, 3), (5, 7), (4, 4)])
group_2 = np.array([(0, 0), (1, 2), (2, 2), (3, 3)])
test_elements_x = [1, 3, 5]
test_elements_y = [2, 3, 3]
test_elements = np.array(list(zip(test_elements_x, test_elements_y)))


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


@pytest.mark.parametrize(
    "group, expected",
    [
        (group_1, [True, True, False]),
        (group_2, [True, True, False]),
    ])
def test_numba(group, expected):
    mask = filter_lumis(test_elements, group)
    assert mask.tolist() == expected
