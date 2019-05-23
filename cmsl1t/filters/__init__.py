import numpy as np

from .muonfilter import muonfilter
from .luminosity import LuminosityFilter
from .pfMetFilter import pfMetFilter


def __combine_with_AND_vectorized(filters, size):
    # for vectorized filters, this dimension are events
    for f in filters:
        yield np.all(f)


def __combine_with_OR_vectorized(filters, size):
    # for vectorized filters, this dimension are events
    for f in filters:
        yield np.any(f)


def combine_with_AND(filters):
    size = np.size(filters[0])
    if size > 1:
        return list(__combine_with_AND_vectorized(filters, size))
    result = True
    for f in filters:
        result = result & f
    return result


def combine_with_OR(filters):
    size = np.size(filters[0])
    if size > 1:
        return list(__combine_with_OR_vectorized(filters, size))
    result = False
    for f in filters:
        result = result | f
    return result


def create_event_mask(filters, method=combine_with_AND):
    if not filters:
        return []
    return method(filters)


__all__ = [
    'combine_with_AND',
    'combine_with_OR',
    'create_event_mask',
    'muonfilter',
    'LuminosityFilter',
    'pfMetFilter',
]
