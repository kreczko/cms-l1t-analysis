from __future__ import print_function
from collections import defaultdict
from rootpy.plotting.hist import Hist1D, Hist2D
from cmsl1t.hist import BaseHistogram
from cmsl1t.hist.factory import HistFactory


class DummyHist(BaseHistogram):

    def __init__(self, name, title):
        super(DummyHist, self).__init__(name, title)
        self.bins = defaultdict(int)

    def fill(self, value, weight=1):
        self.bins[int(value)] += weight


def test_build_rootpy_hist():
    factory = HistFactory("Hist1D", 10, 0, 1,
                          name="test_Hist1D",
                          title="This is just another test")
    hist = factory()
    assert hist.InheritsFrom(Hist1D.Class())

    factory = HistFactory("Hist2D", 10, 0, 1, 10, 2, 5,
                          name="test_Hist2D",
                          title="This is just a test")
    hist = factory()
    assert hist.InheritsFrom(Hist2D.Class())


def test_build_custom_hist():
    factory = HistFactory("DummyHist",
                          name="test_DummyHist",
                          title="This is just yet another test")
    hist = factory()
    assert isinstance(hist, DummyHist)
