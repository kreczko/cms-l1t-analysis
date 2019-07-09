# import aghast
import awkward
import boost.histogram as bh
import numpy as np


def test_fill():
    pileup_bins = [0, 10, 15, 20, 30, 999]
    jet_pt_bins = [35, 90, 120]
    hist = bh.histogram(
        bh.axis.variable(pileup_bins),
        bh.axis.variable(jet_pt_bins, bh.storage.weight()),
    )

    ets = awkward.fromiter([
        np.random.poisson(30, 5),
        np.random.poisson(30, 2),
        np.random.poisson(30, 3),
    ])
    repeat = ets.stops - ets.starts

    weights = np.ones(len(ets))
    weights = np.repeat(weights, repeat, axis=0)
    pileup = np.random.poisson(50, len(ets))
    pileup = np.repeat(pileup, repeat, axis=0)
    # expand pileup to size ets
    assert len(pileup) == len(ets.content)
    # hist.fill(pileup, ets.content, bh.weight(weights))
    hist(pileup, ets.content)
