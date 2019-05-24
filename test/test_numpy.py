import numpy as np

element = [(1, 2), (3, 3), (5, 7)]
test_elements_x = [1, 3, 5]
test_elements_y = [2, 3, 3]
test_elements = list(zip(test_elements_x, test_elements_y))


def test_np_isin():
    isin = np.isin(element, test_elements, assume_unique=True)
    mask = np.all(isin, axis=1)
    assert mask.tolist() == [True, True, False]
