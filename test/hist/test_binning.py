from hypothesis import given, settings, strategies as st
import numpy as np
import pytest
import cmsl1t.hist.binning as binning


@pytest.mark.parametrize(
    'use_everything_bin, n_extra_bins',
    [
        (False, 2),
        (True, 3),
    ]
)
def test_binning_base(use_everything_bin, n_extra_bins):
    n_bins = 10
    b = binning.Base(n_bins, 'test', use_everything_bin=use_everything_bin)
    assert len(b.values) == (n_bins + n_extra_bins)


def test_find_all_bins():
    b = binning.Base(10, 'test')
    pytest.raises(AttributeError, b.find_all_bins, 'overflow')


# @raises(AttributeError)
def test_get_bin_upper():
    b = binning.Base(10, 'test')
    for name in ['overflow', 'underflow', 'everything']:
        assert b.get_bin_upper(name) == name


def test_get_bin_upper_invalid():
    b = binning.Base(10, 'test')
    pytest.raises(AttributeError, b.get_bin_upper, 0)


def test_get_bin_lower():
    b = binning.Base(10, 'test')
    for name in ['overflow', 'underflow', 'everything']:
        assert b.get_bin_lower(name) == name


def test_get_bin_lower_invalid():
    b = binning.Base(10, 'test')
    pytest.raises(AttributeError, b.get_bin_lower, 0)


@given(st.one_of(
    st.lists(st.integers()),
    st.tuples(st.integers()),
    st.lists(st.tuples(st.integers(), st.integers())),
)
)
@settings(max_examples=100)
def test_sorted(bins):
    b = binning.Sorted(bins, 'test')
    assert b.bins == sorted(bins)


@given(st.one_of(
    st.lists(st.integers()).map(sorted),
    st.tuples(st.integers()).map(sorted),
    st.lists(st.tuples(st.integers(), st.integers())).map(sorted),
)
)
@settings(max_examples=100)
def test_get_bin_edges(bins):
    b = binning.Sorted(bins, 'test')
    for i in range(len(bins) - 1):
        assert b.get_bin_upper(i) == bins[i + 1]
        assert b.get_bin_lower(i) == bins[i]

    assert b.get_bin_lower(binning.Base.underflow) == binning.Base.underflow
    assert b.get_bin_lower(binning.Base.overflow) == binning.Base.overflow
    assert b.get_bin_lower(binning.Base.everything) == binning.Base.everything
