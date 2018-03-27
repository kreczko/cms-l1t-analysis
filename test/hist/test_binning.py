import pytest
import cmsl1t.hist.binning as binning


def test_binning_base():
    n_bins = 10
    label = 'test'
    b = binning.Base(n_bins, label, use_everything_bin=False)
    assert len(b.values) == (n_bins + 2)

    b = binning.Base(n_bins, label, use_everything_bin=True)
    assert len(b.values) == (n_bins + 3)


def test_find_all_bins():
    b = binning.Base(10, 'test')
    pytest.raises(AttributeError, b.find_all_bins, 'overflow')


# @raises(AttributeError)
def test_get_bin_upper():
    b = binning.Base(10, 'test')
    assert b.get_bin_upper('overflow') == 'overflow'
    assert b.get_bin_upper('underflow') == 'underflow'
    assert b.get_bin_upper('everything') == 'everything'


def test_get_bin_upper_invalid():
    b = binning.Base(10, 'test')
    pytest.raises(AttributeError, b.get_bin_upper, 0)


def test_get_bin_lower():
    b = binning.Base(10, 'test')
    assert b.get_bin_lower('overflow') == 'overflow'
    assert b.get_bin_lower('underflow') == 'underflow'
    assert b.get_bin_lower('everything') == 'everything'


def test_get_bin_lower_invalid():
    b = binning.Base(10, 'test')
    pytest.raises(AttributeError, b.get_bin_lower, 0)


def test_sorted():
    bins = [40, 60, 80, 99, 111]
    unsorted_bins = [80, 99, 111, 40, 60]

    b = binning.Sorted(bins, 'test')
    assert b.bins == bins

    b = binning.Sorted(unsorted_bins, 'test')
    assert b.bins == bins


def test_get_bin_edges():
    bins = [40, 60, 80, 99, 111]

    b = binning.Sorted(bins, 'test')
    assert b.get_bin_upper(2) == bins[3]
    assert b.get_bin_lower(2) == bins[2]

    assert b.get_bin_lower(binning.Base.underflow) == binning.Base.underflow
    assert b.get_bin_lower(binning.Base.overflow) == binning.Base.overflow
    assert b.get_bin_lower(binning.Base.everything) == binning.Base.everything
