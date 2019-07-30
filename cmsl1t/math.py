import numpy as np


def cumulative_sum_and_error(hist):
    '''
        Takes a histogram and returns an array of cumulative sums of it with
        the total first.
        E.g.
        histogram entries: [1, 2, 3, 4]
        histogram errors: [1, 1, 2, 2]
        Output: [10, 9, 7, 4], [3.16227766, 3, 2.82842712, 2]
    '''
    hist_values = [b.value for b in hist]
    reversed_cumsum = _reversed_cumulative_sum(hist_values)

    errors_squared = np.square([b.error for b in hist])
    reversed_cumsum_errors = np.sqrt(_reversed_cumulative_sum(errors_squared))

    return reversed_cumsum, reversed_cumsum_errors


def _reversed_cumulative_sum(values):
    reversed_values = np.array(np.flipud(values))
    cumsum = np.cumsum(reversed_values)
    reversed_cumsum = np.array(np.flipud(cumsum))
    return reversed_cumsum


def view1D(a, b):
    """
        From https://stackoverflow.com/a/45313353/
    """
    a = np.ascontiguousarray(a)
    b = np.ascontiguousarray(b)
    void_dt = np.dtype((np.void, a.dtype.itemsize * a.shape[1]))
    return a.view(void_dt).ravel(),  b.view(void_dt).ravel()


def isin_nd(a, b):
    """
        From https://stackoverflow.com/questions/54791950
    """
    # a,b are the 3D input arrays to give us "isin-like" functionality across them
    A, B = view1D(a.reshape(a.shape[0], -1), b.reshape(b.shape[0], -1))
    return np.isin(A, B)
