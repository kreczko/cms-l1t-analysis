import pytest

import awkward
import numpy as np

from cmsl1t.jet import Jet


@pytest.fixture
def jetArray():
    ets = awkward.fromiter([
        np.random.poisson(30, 5),
        np.random.poisson(30, 2),
        np.random.poisson(30, 3),
    ]
    )
    etas = awkward.fromiter(
        [
            np.random.normal(0, size=5) * 2.0,
            np.random.normal(0, size=2) * 2.0,
            np.random.normal(0, size=3) * 2.0,
        ]
    )
    phis = awkward.fromiter(
        [
            np.random.normal(0, size=5),
            np.random.normal(0, size=2),
            np.random.normal(0, size=3),
        ]
    )
    return [ets, etas, phis]


def test_jet(jetArray):
    jet = Jet(*jetArray)
    assert len(jet.et.content) == 5 + 2 + 3
    assert len(jet.eta.content) == 5 + 2 + 3
    assert len(jet.phi.content) == 5 + 2 + 3
    assert len(jet.etCorr.content) == 5 + 2 + 3
    assert len(jet.et) == 3
    assert len(jet.eta) == 3
    assert len(jet.phi) == 3
    assert len(jet.etCorr) == 3
