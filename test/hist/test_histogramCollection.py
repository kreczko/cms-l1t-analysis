from __future__ import print_function
import cmsl1t.hist.hist_collection as hist
import cmsl1t.hist.binning as binning
import numpy as np
from cmsl1t.hist.factory import HistFactory


pileup = binning.Sorted([0, 10, 15, 20, 30, 999], "pileup")
multi = binning.Overlapped([(0, 10), (100, 110), (5, 15)], "multi")
regions = binning.EtaRegions()


class dummy_factory():
    instance_count = 0

    def __init__(self, *vargs, **kwargs):
        dummy_factory.instance_count += 1
        self.count = 0
        self.value = 0
        self.bin_labels = vargs

    def __call__(self):
        print("making histogram:", dummy_factory.instance_count, self.count)
        self.count += 1

    def fill(self, weight=1):
        self.value += weight


def test_dimension_sorted():
    assert pileup.find_bins(-19) == [binning.Base.underflow]
    assert pileup.find_bins(9) == [0]
    assert pileup.find_bins(19) == [2]
    assert pileup.find_bins(39) == [4]
    assert pileup.find_bins(9999) == [binning.Base.overflow]


def test_dimension_multi():
    assert multi.find_bins(3) == [0]
    assert multi.find_bins(7) == [0, 2]
    assert multi.find_bins(105) == [1]
    assert multi.find_bins(70) == [binning.Base.overflow]


def test_dimension_region():
    assert sorted(regions.find_bins(0)) == sorted(["BE", "B"])
    assert sorted(regions.find_bins(2)) == sorted(["BE", "E"])
    assert regions.find_bins(3.1) == ["HF"]


def test_flatten_bin_list():
    bin_list = [[1]]
    flat_list = hist.HistogramCollection._flatten_bins(bin_list)
    assert flat_list == [(1, )]
    bin_list = [[1], [2, 3]]
    flat_list = hist.HistogramCollection._flatten_bins(bin_list)
    assert flat_list == [(1, 2), (1, 3)]


def test_find_bins():
    coll = hist.HistogramCollection(dimensions=[pileup],
                                    histogram_factory=dummy_factory)
    assert coll._find_bins(-20) == [(binning.Base.underflow, )]
    assert coll._find_bins(13) == [(1, )]
    assert coll._find_bins(47) == [(4, )]
    assert coll._find_bins(9999) == [(binning.Base.overflow, )]


def test_collection_1D():
    coll = hist.HistogramCollection(dimensions=[pileup],
                                    histogram_factory=dummy_factory)
    coll[-3].fill(6)
    coll[11].fill(2)
    coll[42].fill(42)
    coll[10044].fill(49)
    assert coll[-20].value == [6]
    assert coll[13].value == [2]
    assert coll[47].value == [42]
    assert coll[9999].value == [49]


def test_collection_2D():
    coll = hist.HistogramCollection(dimensions=[pileup, multi],
                                    histogram_factory=dummy_factory)
    coll[-3, 4].fill(6)
    coll[11, 105].fill(49)
    assert coll[-20, 2].value == [6]
    assert coll[13, 108].value == [49]


def test_iteration_2D():
    coll = hist.HistogramCollection(dimensions=[pileup, multi],
                                    histogram_factory=dummy_factory)

    all_bins = []
    for i_first in coll:
        rows = []
        for i_second in coll.get_bin_contents([i_first]):
            rows.append([i_first, i_second])
            coll.get_bin_contents([i_first, i_second]).fill(1)
        all_bins.append(rows)
    all_bins = np.array(all_bins)

    total = 0
    for i_first in coll:
        for i_second in coll.get_bin_contents([i_first]):
            total += coll.get_bin_contents([i_first, i_second]).value

    assert all_bins.shape == (len(pileup), len(multi), 2)
    assert total == len(pileup) * len(multi)
    assert coll[3, 13].value == [1]


def test_coll1D_root_Hist1D():
    histogram_factory = HistFactory("Hist1D", 10, 0, 5)
    coll = hist.HistogramCollection(dimensions=[pileup],
                                    histogram_factory=histogram_factory)
    coll[13].fill(1)
    coll[11].fill(2)
    integral = sum([h.Integral() for h in coll[12]])
    assert integral == 2
