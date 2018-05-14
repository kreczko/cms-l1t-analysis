
from .luminosity import LuminosityFilter
from .pfMetFilter import pfMetFilter


def muonfilter(muons):
    passes = False
    for muon in muons:
        if muon.pt > 20 and muon.iso <= 0.1 and bool(muon.isLooseMuon):
            passes = True
            break
    return passes
