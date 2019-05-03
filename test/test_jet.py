from cmsl1t.jet import Jet, CaloJet, PFJet


def test_jet():
    jet = Jet(30, 0, 2)
    assert jet.et == 30
    assert jet.eta == 0
    assert jet.phi == 2


def test_calojet():
    jet = CaloJet(30, 0, 2, 31.2)
    assert jet.et == 30
    assert jet.etCorr == 31.2
    assert jet.eta == 0
    assert jet.phi == 2


def test_pfjet():
    values = [30, 0, 2, 31.2, 1, 2, 3, 4, 5, 6, 7, 8]
    jet = PFJet(*values)
    assert jet.et == 30
    assert jet.etCorr == 31.2
    assert jet.eta == 0
    assert jet.phi == 2

    assert jet.cemef == 1
    assert jet.chef == 2
    assert jet.cMult == 3
    assert jet.mef == 4
    assert jet.muMult == 5
    assert jet.nemef == 6
    assert jet.nhef == 7
    assert jet.nMult == 8
