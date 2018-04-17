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
